const API_URL = "http://127.0.0.1:8000/api";
const USER_ID = 1;

document.addEventListener("DOMContentLoaded", fetchGroceryList);

async function fetchGroceryList() {
    try {
        const response = await fetch(`${API_URL}/users/${USER_ID}/grocery-list`);
        const data = await response.json();

        const tableBody = document.getElementById("grocery-table-body");
        tableBody.innerHTML = "";

        if (data.grocery_list && data.grocery_list.length > 0) {
            data.grocery_list.forEach(item => {
                const row = document.createElement("tr");
                row.innerHTML = `
                    <td>${item.ingredient_name || 'Ingredient #' + item.ingredient_id}</td>
                    <td><strong>${item.needed_amount}</strong></td>
                    <td>${item.unit}</td>
                `;
                tableBody.appendChild(row);
            });
        } else {
            tableBody.innerHTML = `<tr><td colspan="3" style="text-align:center;">Your pantry has all required ingredients!</td></tr>`;
        }
    } catch (error) {
        console.error("Error fetching grocery list:", error);
    }
}