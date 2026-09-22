const API_URL = "http://127.0.0.1:8000/api";

document.getElementById("recipe-form").addEventListener("submit", async (e) => {
    e.preventDefault();

    const ingredientsInput = document.getElementById("recipe-ingredients").value;
    const resultBox = document.getElementById("recipe-result");

    resultBox.innerText = "Generating recipe using AI model... Please wait...";

    try {
        const response = await fetch(`${API_URL}/suggest-recipe`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ ingredients: ingredientsInput })
        });

        const data = await response.json();

        if (response.ok) {
            resultBox.innerHTML = `
                <div style="margin-bottom: 1rem;">
                    <img src="${data.image_url}" id="recipe-image" alt="Recipe Food" style="width:100%; max-height:220px; object-fit:cover; border-radius:8px;">
                </div>
                <div>${data.recipe}</div>
            `;
        } else {
            resultBox.innerText = "Failed to generate recipe. " + (data.detail || "");
        }
    } catch (error) {
        console.error("Error suggesting recipe:", error);
        resultBox.innerText = "Connection error with server.";
    }
});