const API_URL = "http://127.0.0.1:8000/api";

document.addEventListener('DOMContentLoaded', () => {
    const dietForm = document.getElementById('diet-form');
    const dietResult = document.getElementById('diet-result');

    if (dietForm) {
        dietForm.addEventListener('submit', async (e) => {
            e.preventDefault();

            const weightVal = parseFloat(document.getElementById('diet-weight').value);
            const heightVal = parseFloat(document.getElementById('diet-height').value);
            const ageVal = parseInt(document.getElementById('diet-age').value);
            const genderVal = document.getElementById('diet-gender').value;

            const formData = {
                weight: weightVal,
                height: heightVal,
                age: ageVal,
                gender: genderVal,
                activity_level: "moderate",
                goal: "weight loss",
                diet_type: "Balanced"
            };

            if (dietResult) {
                dietResult.innerText = "Generating your personalized plan...";
            }

            try {
                const response = await fetch(`${API_URL}/create-diet`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(formData)
                });

                if (!response.ok) {
                    throw new Error('Failed to generate diet plan');
                }

                const data = await response.json();

                if (data.status === 'success' || data.diet_plan) {
                    if (dietResult) {
                        dietResult.innerText = data.diet_plan || data.message;
                    }
                } else {
                    if (dietResult) {
                        dietResult.innerText = "Error: Could not generate plan. Please check your input.";
                    }
                }
            } catch (error) {
                console.error('Error generating diet plan:', error);
                if (dietResult) {
                    dietResult.innerText = "Something went wrong. Please check if the server is running.";
                }
            }
        });
    }
});
