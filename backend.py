from fastapi import FastAPI, Depends, HTTPException , status
from pydantic import BaseModel , ConfigDict
from sqlalchemy import Column, Integer, String, Boolean , Date 
from sqlalchemy.orm import Session
from db import Base, engine, get_db
from datetime import date
from typing import Optional
from decimal import Decimal

app=FastAPI()

class Users(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)

class UserCreate(BaseModel):
    username: str
    email: str

class UserResponse(BaseModel):
    user_id: int
    username: str
    email: str

    class Config:
        from_attributes = True

class Recipe(Base):
  __tablename__ = "Recipe"

  recipe_id = Column(Integer, primary_key=True, index=True)
  user_id = Column(Integer)
  name = Column(String(255))
  instructions = Column(String(1000))
  servings = Column(Integer)
  prep_time = Column(Integer)


class RecipeCreate(BaseModel):
  user_id: Optional[int] = None
  name: str
  instructions: Optional[str] = None
  servings: Optional[int] = None
  prep_time: Optional[int] = None


class RecipeResponse(BaseModel):
  recipe_id: int
  user_id: Optional[int] = None
  name: str
  instructions: Optional[str] = None
  servings: Optional[int] = None
  prep_time: Optional[int] = None

  class Config:
    from_attributes = True


class Aisle(Base):
  __tablename__ = "aisles"

  aisle_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
  name = Column(String(50), nullable=False)


class AisleCreate(BaseModel):
  name: str


class AisleResponse(BaseModel):
  aisle_id: int
  name: str

  class Config:
    from_attributes = True

class Ingredient(Base):
  __tablename__ = "ingredients"

  ingredient_id = Column(
      Integer, primary_key=True, index=True, autoincrement=True
  )
  name = Column(String(100), nullable=False)
  quantity = Column(Integer, nullable=False)
  unit = Column(String(50), nullable=False)

class IngredientCreate(BaseModel):
    name: str
    quantity: Decimal
    unit: str


class IngredientResponse(BaseModel):
    ingredient_id: int
    name: str
    quantity: Decimal
    unit: str

    model_config = ConfigDict(from_attributes=True)

@app.get("/aisles", response_model=list[AisleResponse])
def get_all_aisles(db: Session = Depends(get_db)):
  return db.query(Aisle).all()


class RecipeIngredients(Base):
   __tablename__ = "recipeingredients"

   recipe_ingredient_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
   recipe_id = Column(Integer, nullable=False)
   ingredient_id = Column(Integer, nullable=False)
   quantity = Column(Integer, nullable=False)
   unit = Column(String(50), nullable=False)


class RecipeIngredientsCreate(BaseModel):
   ingredient_id: int
   quantity: float
   unit: str

class RecipeIngredientsResponse(BaseModel):
   recipe_ingredient_id: int
   recipe_id: int
   ingredient_id: int
   quantity: float
   unit: str

   class Config:
       from_attributes = True

class PantryItem(Base):
   __tablename__ = "pantryitem"

   pantry_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
   user_id = Column(Integer, nullable=False)
   ingredient_id = Column(Integer, nullable=False)
   quantity = Column(Integer, nullable=False)

class PantryItemCreate(BaseModel):
   ingredient_id: int
   quantity: float

class PantryItemResponse(BaseModel):
    pantry_id: int
    user_id: int
    ingredient_id: int
    quantity: float

    class Config:
        from_attributes = True

class MealPlanEntry(Base):
    __tablename__ = "mealplanentry"

    entry_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, index=True)
    recipe_id = Column(Integer, index=True)
    planned_date = Column(Date, nullable=False )
    meal_slote = Column(String(50), nullable=False)  # e.g., breakfast, lunch, dinner
   

#GroceryListItem: item_id (PK), user_id, ingredient_id, quantity_needed, is_checked

class GroceryListItem(Base):
    __tablename__ = "grocerylistitem"

    item_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, index=True)
    ingredient_id = Column(Integer, index=True)
    quantity_needed = Column(Integer, default=0)
    is_checked = Column(Boolean, default=False)


Base.metadata.create_all(bind=engine)

class MealPlanEntryCreate(BaseModel):
    user_id: int
    recipe_id: int
    planned_date: date
    meal_slote: str

class MealPlanEntryResponse(BaseModel):
    entry_id:int
    user_id:int
    recipe_id:int
    planned_date:date
    meal_slote:str

    class Config:
        from_attributes = True

class MealPlanEntryUpdate(BaseModel):
    user_id:int= None
    recipe_id:int= None
    planned_date:date= None
    meal_slote:str= None

class GroceryListItemCreate(BaseModel):
    user_id:int
    ingredient_id:int
    quantity_needed:int

class GroceryListItemUpdate(BaseModel):
    quantity_needed: int
    is_checked: bool

class GroceryListItemResponse(BaseModel):
    item_id: int
    user_id: int
    ingredient_id: int
    quantity_needed: int
    is_checked: bool

    class Config:
        from_attributes = True


app = FastAPI()

from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/users", response_model=UserResponse, status_code=201)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = Users(username=user.username, email=user.email)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@app.get("/users", response_model=list[UserResponse])
def get_all_users(db: Session = Depends(get_db)):
    return db.query(Users).all()

#mealplanentry end points

@app.get("/mealplanentry", response_model=list[MealPlanEntryResponse])
def get_all_mealplan_entry(db: Session = Depends(get_db)):
    return db.query(MealPlanEntry).all()

@app.post("/mealplanentry", response_model=MealPlanEntryResponse)
def create_mealplan_entry(mealplan: MealPlanEntryCreate, db: Session = Depends(get_db)):
    db_mealplan = MealPlanEntry(
        user_id=mealplan.user_id,
        recipe_id=mealplan.recipe_id,
        planned_date=mealplan.planned_date,
        meal_slote=mealplan.meal_slote
    )
    db.add(db_mealplan)
    db.commit()
    db.refresh(db_mealplan)
    return db_mealplan

@app.put("/mealplanentry/{entry_id}", response_model=MealPlanEntryResponse)
def update_mealplan_entry(entry_id: int, data: MealPlanEntryUpdate, db: Session = Depends(get_db)):
    db_mealplan = db.query(MealPlanEntry).filter(MealPlanEntry.entry_id == entry_id).first()
    if not db_mealplan:
        raise HTTPException(status_code=404, detail="Meal plan entry not found")

    for key, value in data.dict(exclude_unset=True).items():
        setattr(db_mealplan, key, value)
    db.commit()
    db.refresh(db_mealplan)
    return db_mealplan

@app.delete("/mealplanentry/{entry_id}")
def delete_mealplan_entry(entry_id: int, db: Session = Depends(get_db)):
    db_mealplan = db.query(MealPlanEntry).filter(MealPlanEntry.entry_id == entry_id).first()
    if not db_mealplan:
        raise HTTPException(status_code=404, detail="Meal plan entry not found")
    
    db.delete(db_mealplan)
    db.commit()
    return {"message": "Meal plan entry deleted successfully"}

#grocery list endpoints

@app.get("/grocerylistitems", response_model=list[GroceryListItemResponse])
def get_all_grocery_list_items(db: Session = Depends(get_db)):
    return db.query(GroceryListItem).all()

@app.post("/grocerylistitems", response_model=GroceryListItemResponse)
def create_grocery_list_item(item: GroceryListItemCreate, db: Session = Depends(get_db)):
    db_item = GroceryListItem(
        user_id=item.user_id,
        ingredient_id=item.ingredient_id,
        quantity_needed=item.quantity_needed,
    )
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

@app.put("/grocerylistitem/{item_id}", response_model=GroceryListItemResponse)
def update_grocery_list_item(item_id: int, data: GroceryListItemUpdate, db: Session = Depends(get_db)):
    db_item = db.query(GroceryListItem).filter(GroceryListItem.item_id == item_id).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="Grocery list item not found")

    for key, value in data.dict(exclude_unset=True).items():
        setattr(db_item, key, value)
    db.commit()
    db.refresh(db_item)
    return db_item

@app.delete("/grocerylistitem/{item_id}")
def delete_grocery_list_item(item_id: int, db: Session = Depends(get_db)):
    db_item = db.query(GroceryListItem).filter(GroceryListItem.item_id == item_id).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="Grocery List Item entry not found")
    
    db.delete(db_item)
    db.commit()
    return {"message": "Grocery list item deleted successfully"}

#recipe ingredients endpoints

@app.post("/recipes/{recipe_id}/ingredients", response_model=RecipeIngredientsResponse, status_code=201)
def add_ingredient_to_recipe(recipe_id: int, item: RecipeIngredientsCreate, db: Session = Depends(get_db)):
   db_item = RecipeIngredients(recipe_id=recipe_id, **item.dict())
   db.add(db_item)
   db.commit()
   db.refresh(db_item)
   return db_item

@app.get("/recipes/{recipe_id}/ingredients", response_model=list[RecipeIngredientsResponse])
def get_recipe_ingredients(recipe_id: int, db: Session = Depends(get_db)):
    return db.query(RecipeIngredients).filter(RecipeIngredients.recipe_id == recipe_id).all()

#pantryitem end points 

@app.post("/users/{user_id}/pantry", response_model=PantryItemResponse, status_code=201)
def add_to_pantry(user_id: int, item: PantryItemCreate, db: Session = Depends(get_db)):
    db_item = PantryItem(user_id=user_id, **item.dict())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

@app.get("/users/{user_id}/pantry", response_model=list[PantryItemResponse])
def get_user_pantry(user_id: int, db: Session = Depends(get_db)):
    return db.query(PantryItem).filter(PantryItem.user_id == user_id).all()

@app.delete("/pantry/{pantry_id}")
def delete_from_pantry(pantry_id: int, db: Session = Depends(get_db)):
    db_item = db.query(PantryItem).filter(PantryItem.pantry_id == pantry_id).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")
    db.delete(db_item)
    db.commit()
    return {"message": "Item removed from pantry successfully"}

#aisles end points

@app.post("/aisles", response_model=AisleResponse, status_code=201)
def create_aisle(aisle: AisleCreate, db: Session = Depends(get_db)):
  db_aisle = Aisle(name=aisle.name)
  db.add(db_aisle)
  db.commit()
  db.refresh(db_aisle)
  return db_aisle

#recipes end points

@app.get("/recipes", response_model=list[RecipeResponse])
def get_all_recipes(db: Session = Depends(get_db)):
  return db.query(Recipe).all()


@app.get("/recipes/{recipe_id}", response_model=RecipeResponse)
def get_recipe(recipe_id: int, db: Session = Depends(get_db)):
  recipe = (
      db.query(Recipe).filter(Recipe.recipe_id == recipe_id).first()
  )
  if not recipe:
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, detail="Recipe not found"
    )
  return recipe


@app.post(
    "/recipes",
    response_model=RecipeResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_recipe(recipe: RecipeCreate, db: Session = Depends(get_db)):
  try:
    new_recipe = Recipe(
        user_id=recipe.user_id,
        name=recipe.name,
        instructions=recipe.instructions,
        servings=recipe.servings,
        prep_time=recipe.prep_time,
    )
    db.add(new_recipe)
    db.commit()
    db.refresh(new_recipe)
    return new_recipe
  except Exception as e:
    db.rollback()
    raise HTTPException(
        status_code=500, detail=f"Database error: {str(e)}"
    )


@app.put("/recipes/{recipe_id}", response_model=RecipeResponse)
def update_recipe(
    recipe_id: int, recipe: RecipeCreate, db: Session = Depends(get_db)
):
  existing_recipe = (
      db.query(Recipe).filter(Recipe.recipe_id == recipe_id).first()
  )
  if not existing_recipe:
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, detail="Recipe not found"
    )

  existing_recipe.user_id = recipe.user_id
  existing_recipe.name = recipe.name
  existing_recipe.instructions = recipe.instructions
  existing_recipe.servings = recipe.servings
  existing_recipe.prep_time = recipe.prep_time

  db.commit()
  db.refresh(existing_recipe)
  return existing_recipe


@app.delete("/recipes/{recipe_id}")
def delete_recipe(recipe_id: int, db: Session = Depends(get_db)):
  recipe = (
      db.query(Recipe).filter(Recipe.recipe_id == recipe_id).first()
  )
  if not recipe:
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, detail="Recipe not found"
    )

  db.delete(recipe)
  db.commit()
  return {"message": "Recipe deleted successfully"}


#ingredients end points 
@app.post("/ingredients", response_model=IngredientResponse, status_code=201)
def create_ingredient(
    ingredient: IngredientCreate, db: Session = Depends(get_db)
):
  new_ingredient = Ingredient(
      name=ingredient.name, quantity=ingredient.quantity, unit=ingredient.unit
  )
  db.add(new_ingredient)
  db.commit()
  db.refresh(new_ingredient)
  return new_ingredient


@app.get("/ingredients", response_model=list[IngredientResponse])
def get_ingredients(db: Session = Depends(get_db)):
  return db.query(Ingredient).all()


@app.get("/ingredients/{ingredient_id}", response_model=IngredientResponse)
def get_ingredient(ingredient_id: int, db: Session = Depends(get_db)):
  ingredient = (
      db.query(Ingredient).filter(Ingredient.ingredient_id == ingredient_id)
      .first()
  )
  if not ingredient:
    raise HTTPException(status_code=404, detail="Ingredient not found")
  return ingredient


@app.put("/ingredients/{ingredient_id}", response_model=IngredientResponse)
def update_ingredient(
    ingredient_id: int, data: IngredientCreate, db: Session = Depends(get_db)
):
  ingredient = (
      db.query(Ingredient).filter(Ingredient.ingredient_id == ingredient_id)
      .first()
  )
  if not ingredient:
    raise HTTPException(status_code=404, detail="Ingredient not found")

  ingredient.name = data.name
  ingredient.quantity = data.quantity
  ingredient.unit = data.unit

  db.commit()
  db.refresh(ingredient)
  return ingredient


@app.delete("/ingredients/{ingredient_id}")
def delete_ingredient(ingredient_id: int, db: Session = Depends(get_db)):
  ingredient = (
      db.query(Ingredient).filter(Ingredient.ingredient_id == ingredient_id)
      .first()
  )
  if not ingredient:
    raise HTTPException(status_code=404, detail="Ingredient not found")

  db.delete(ingredient)
  db.commit()
  return {"message": "Ingredient deleted successfully"}
