from flask import Flask, jsonify, request

app = Flask(__name__)

pantry_inventory = {
    "tomatoes": {"qty": 2, "unit": "items", "aisle": "Produce"},
    "pasta": {"qty": 1, "unit": "box", "aisle": "Pantry"}
}

@app.route('/api/pantry', methods=['GET'])
def get_pantry():
    return jsonify(pantry_inventory)

@app.route('/api/generate-shopping-list', methods=['POST'])
def generate_list():
    selected_meals = request.json.get('meals', [])
    needed_ingredients = {}

    for meal in selected_meals:
        for item in meal.get('ingredients', []):
            name = item['name']
            needed_qty = item['quantity']
            aisle = item['aisle']

            pantry_qty = pantry_inventory.get(name, {}).get('qty', 0)
            missing_qty = max(0, needed_qty - pantry_qty)

            if missing_qty > 0:
                if aisle not in needed_ingredients:
                    needed_ingredients[aisle] = []
                needed_ingredients[aisle].append({"item": name, "qty": missing_qty})

    return jsonify({"shopping_list": needed_ingredients})

if __name__ == '__main__':
    app.run(debug=True, port=5000)