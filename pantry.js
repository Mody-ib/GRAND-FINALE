const API_URL = "http://127.0.0.1:8000/api";
const USER_ID = 1;

document.addEventListener("DOMContentLoaded", fetchPantryItems);

async function fetchPantryItems() {
    try {
        const response = await fetch(`${API_URL}/users/${USER_ID}/pantry`);
        const data = await response.json();
        
        const tableBody = document.getElementById("pantry-table-body");
        tableBody.innerHTML = "";

        if (Array.isArray(data) && data.length > 0) {
            data.forEach(item => {
                const row = document.createElement("tr");
                row.innerHTML = `
                    <td>${item.id}</td>
                    <td>${item.ingredient_name || 'Ingredient #' + item.id}</td>
                    <td>${item.amount}</td>
                    <td>${item.unit}</td>
                    <td>
                        <button style="color: var(--danger-red); border:none; background:none; cursor:pointer;" onclick="deletePantryItem(${item.id})">Remove</button>
                    </td>
                `;
                tableBody.appendChild(row);
            });
        } else {
            tableBody.innerHTML = `<tr><td colspan="5" style="text-align:center;">No items in your pantry.</td></tr>`;
        }
    } catch (error) {
        console.error("Error fetching pantry items:", error);
    }
}

document.getElementById("pantry-form").addEventListener("submit", async (e) => {
    e.preventDefault();
    
    const payload = {
        ingredient_id: parseInt(document.getElementById("pantry-ing-id").value),
        amount: parseFloat(document.getElementById("pantry-amount").value),
        unit: document.getElementById("pantry-unit").value
    };

    try {
        const response = await fetch(`${API_URL}/users/${USER_ID}/pantry`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
        });

        if (response.ok) {
            document.getElementById("pantry-form").reset();
            fetchPantryItems();
        }
    } catch (error) {
        console.error("Error adding pantry item:", error);
    }
});

async function deletePantryItem(pantryId) {
    try {
        const response = await fetch(`${API_URL}/pantry/${pantryId}`, {
            method: "DELETE"
        });

        if (response.ok) {
            fetchPantryItems();
        }
    } catch (error) {
        console.error("Error deleting pantry item:", error);
    }
}