from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel
from typing import Optional
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from db import get_db_connection

app = FastAPI()

model_name = "Qwen/Qwen2.5-0.5B-Instruct"

tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(
    model_name,
    torch_dtype="auto",
    device_map="auto",
    low_cpu_mem_usage=True
)


class SuggestRecipeRequest(BaseModel):
    ingredients: str


class CreateDietRequest(BaseModel):
    weight: float
    height: float
    age: int
    gender: str
    activity_level: Optional[str] = "moderate"
    goal: Optional[str] = "weight loss"
    diet_type: Optional[str] = "Balanced"


class RecipeIngredientCreate(BaseModel):
    ingredient_id: int
    amount: float
    unit: str
    notes: Optional[str] = ""


class PantryItemCreate(BaseModel):
    ingredient_id: int
    amount: float
    unit: str


@app.post("/api/suggest-recipe")
def suggest_recipe(data: SuggestRecipeRequest):
    if not data.ingredients:
        raise HTTPException(status_code=400, detail="Ingredients list is required")

    prompt = (
        f"Based on these ingredients: ({data.ingredients}), suggest one detailed recipe.\n"
        f"You MUST include:\n"
        f"1. Recipe Name\n"
        f"2. Preparation steps\n"
        f"3. Detailed Nutritional Information (Total Calories, Protein in grams, Carbs in grams, Fats in grams)."
    )
    
    messages = [
        {"role": "system", "content": "You are a professional nutritionist and meal planner. Always provide accurate macro and calorie calculations."},
        {"role": "user", "content": prompt}
    ]
    
    text = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    inputs = tokenizer([text], return_tensors="pt").to(model.device)
    outputs = model.generate(**inputs, max_new_tokens=450)
    
    generated_ids = [
        output_ids[len(input_ids):] for input_ids, output_ids in zip(inputs.input_ids, outputs)
    ]
    recipe_text = tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]
    
    image_url = f"https://source.unsplash.com/featured/?food,{data.ingredients.replace(' ', ',')}"
    
    return {
        "status": "success",
        "recipe": recipe_text,
        "image_url": image_url
    }


@app.post("/api/create-diet")
def create_diet(data: CreateDietRequest):
    prompt = (
        f"Create a custom daily diet plan based on the following body measurements and user info:\n"
        f"- Weight: {data.weight} kg\n"
        f"- Height: {data.height} cm\n"
        f"- Age: {data.age} years old\n"
        f"- Gender: {data.gender}\n"
        f"- Activity Level: {data.activity_level}\n"
        f"- Primary Goal: {data.goal}\n"
        f"- Diet Preference: {data.diet_type}\n\n"
        f"Please perform the following calculations:\n"
        f"1. Daily Target Calories and Total Daily Energy Expenditure (TDEE).\n"
        f"2. Total Daily Macronutrient Breakdown: Protein (g), Carbohydrates (g), and Fats (g).\n"
        f"3. Full meal plan (Breakfast, Lunch, Dinner, Snacks) with calories and macros breakdown for each meal."
    )
    
    messages = [
        {"role": "system", "content": "You are an expert clinical nutritionist. Precise calorie and macro breakdowns are required for all recommendations."},
        {"role": "user", "content": prompt}
    ]
    
    text = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    inputs = tokenizer([text], return_tensors="pt").to(model.device)
    outputs = model.generate(**inputs, max_new_tokens=800)
    
    generated_ids = [
        output_ids[len(input_ids):] for input_ids, output_ids in zip(inputs.input_ids, outputs)
    ]
    plan_text = tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]
    
    return {
        "status": "success",
        "diet_plan": plan_text
    }


@app.post("/api/recipes/{recipe_id}/ingredients", status_code=status.HTTP_201_CREATED)
def add_ingredient_to_recipe(recipe_id: int, item: RecipeIngredientCreate):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        query = """
            INSERT INTO recipe_ingredients (recipe_id, ingredient_id, amount, unit, notes)
            VALUES (%s, %s, %s, %s, %s)
        """
        cursor.execute(query, (recipe_id, item.ingredient_id, item.amount, item.unit, item.notes))
        conn.commit()
        
        new_id = cursor.lastrowid
        cursor.close()
        conn.close()

        return {
            "message": "Ingredient linked to recipe successfully",
            "recipe_ingredient_id": new_id
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/recipes/{recipe_id}/ingredients")
def get_recipe_ingredients(recipe_id: int):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        query = """
            SELECT 
                ri.id AS id,
                i.name AS ingredient_name,
                ri.amount,
                ri.unit,
                ri.notes
            FROM recipe_ingredients ri
            JOIN ingredients i ON ri.ingredient_id = i.id
            WHERE ri.recipe_id = %s
        """
        cursor.execute(query, (recipe_id,))
        ingredients = cursor.fetchall()
        
        cursor.close()
        conn.close()

        return ingredients
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/users/{user_id}/pantry", status_code=status.HTTP_201_CREATED)
def add_to_pantry(user_id: int, item: PantryItemCreate):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        query = """
            INSERT INTO pantry_items (user_id, ingredient_id, amount, unit)
            VALUES (%s, %s, %s, %s)
        """
        cursor.execute(query, (user_id, item.ingredient_id, item.amount, item.unit))
        conn.commit()
        
        new_id = cursor.lastrowid
        cursor.close()
        conn.close()

        return {
            "message": "Item added to pantry successfully",
            "pantry_item_id": new_id
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/users/{user_id}/pantry")
def get_user_pantry(user_id: int):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        query = """
            SELECT 
                p.id AS id,
                i.name AS ingredient_name,
                p.amount,
                p.unit
            FROM pantry_items p
            JOIN ingredients i ON p.ingredient_id = i.id
            WHERE p.user_id = %s
        """
        cursor.execute(query, (user_id,))
        pantry_items = cursor.fetchall()
        
        cursor.close()
        conn.close()

        return pantry_items
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/pantry/{pantry_id}")
def delete_from_pantry(pantry_id: int):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        query = "DELETE FROM pantry_items WHERE id = %s"
        cursor.execute(query, (pantry_id,))
        conn.commit()
        
        cursor.close()
        conn.close()

        return {"message": "Item removed from pantry successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))