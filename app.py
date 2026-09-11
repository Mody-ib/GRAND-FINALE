from fastapi import FastAPI
from pydantic import BaseModel
from typing import List

app = FastAPI()

pantry_inventory = {
    "tomatoes": {"qty": 2, "unit": "items", "aisle": "Produce"},
    "pasta": {"qty": 1, "unit": "box", "aisle": "Pantry"}
}


class Ingredient(BaseModel):
    name: str
    quantity: float
    aisle: str


class Meal(BaseModel):
    ingredients: List[Ingredient] = []


class ShoppingListRequest(BaseModel):
    meals: List[Meal] = []


@app.get('/api/pantry')
def get_pantry():
    return pantry_inventory


@app.post('/api/generate-shopping-list')
def generate_list(request: ShoppingListRequest):
    needed_ingredients = {}

    for meal in request.meals:
        for item in meal.ingredients:
            name = item.name
            needed_qty = item.quantity
            aisle = item.aisle

            pantry_qty = pantry_inventory.get(name, {}).get('qty', 0)
            missing_qty = max(0, needed_qty - pantry_qty)

            if missing_qty > 0:
                if aisle not in needed_ingredients:
                    needed_ingredients[aisle] = []
                needed_ingredients[aisle].append({"item": name, "qty": missing_qty})

    return {"shopping_list": needed_ingredients}


if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)