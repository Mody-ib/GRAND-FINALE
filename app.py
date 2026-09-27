
from flask import request, jsonify
from db import get_db_connection 
from flask import Flask, request, jsonify
from flask_cors import CORS
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

app = Flask(__name__)
CORS(app)

model_name = "Qwen/Qwen2.5-0.5B-Instruct"

tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(
    model_name,
    torch_dtype="auto",
    device_map="auto",
    low_cpu_mem_usage=True
)

@app.route('/api/suggest-recipe', methods=['POST'])
def suggest_recipe():
    data = request.json
    ingredients = data.get('ingredients', '')
    
    if not ingredients:
        return jsonify({"error": "Ingredients list is required"}), 400

    prompt = f"Based on these ingredients: ({ingredients}), suggest one detailed recipe including name, calories, and short preparation steps."
    
    messages = [
        {"role": "system", "content": "You are a professional nutritionist and meal planner."},
        {"role": "user", "content": prompt}
    ]
    
    text = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    inputs = tokenizer([text], return_tensors="pt").to(model.device)
    outputs = model.generate(**inputs, max_new_tokens=300)
    recipe_text = tokenizer.batch_decode(outputs, skip_special_tokens=True)[0]
    
    image_url = f"https://source.unsplash.com/featured/?food,{ingredients.replace(' ', ',')}"
    
    return jsonify({
        "status": "success",
        "recipe": recipe_text,
        "image_url": image_url
    })

@app.route('/api/create-diet', methods=['POST'])
def create_diet():
    data = request.json
    diet_type = data.get('diet_type', 'Balanced')
    calories = data.get('calories', '2000')
    
    prompt = f"Create a complete daily diet plan for {diet_type} with a target of {calories} kcal. Include calories breakdown for Breakfast, Lunch, Dinner, and Snacks."
    
    messages = [
        {"role": "system", "content": "You are a professional nutritionist and meal planner."},
        {"role": "user", "content": prompt}
    ]
    
    text = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    inputs = tokenizer([text], return_tensors="pt").to(model.device)
    outputs = model.generate(**inputs, max_new_tokens=500)
    plan_text = tokenizer.batch_decode(outputs, skip_special_tokens=True)[0]
    
    return jsonify({
        "status": "success",
        "diet_plan": plan_text
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
    

@app.route('/api/recipes/<int:recipe_id>/ingredients', methods=['POST'])
def add_ingredient_to_recipe(recipe_id):
    data = request.get_json()
    ingredient_id = data.get('ingredient_id')
    amount = data.get('amount')
    unit = data.get('unit')
    notes = data.get('notes', '')

    if not ingredient_id or amount is None or not unit:
        return jsonify({"message": "Incomplete ingredient data (ingredient_id, amount, unit are required)"}), 400

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        query = """
            INSERT INTO recipe_ingredients (recipe_id, ingredient_id, amount, unit, notes)
            VALUES (%s, %s, %s, %s, %s)
        """
        cursor.execute(query, (recipe_id, ingredient_id, amount, unit, notes))
        conn.commit()
        
        new_id = cursor.lastrowid
        cursor.close()
        conn.close()

        return jsonify({
            "message": "Ingredient linked to recipe successfully",
            "recipe_ingredient_id": new_id
        }), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500


