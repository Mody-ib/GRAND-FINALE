const API_URL = "http://127.0.0.1:8000/api";

document.getElementById("register-form").addEventListener("submit", async (e) => {
    e.preventDefault();

    const name = document.getElementById("reg-name").value;
    const email = document.getElementById("reg-email").value;
    const password = document.getElementById("reg-password").value;
    const messageBox = document.getElementById("register-message");

    messageBox.style.color = "var(--text-muted)";
    messageBox.innerText = "Creating account...";

    try {
        const response = await fetch(`${API_URL}/register`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ name, email, password })
        });

        const data = await response.json();

        if (response.ok) {
            messageBox.style.color = "var(--primary-emerald)";
            messageBox.innerText = "Registration successful! Redirecting to login...";
            setTimeout(() => {
                window.location.href = "login.html";
            }, 1500);
        } else {
            messageBox.style.color = "var(--danger-red)";
            messageBox.innerText = data.detail || "Registration failed.";
        }
    } catch (error) {
        console.error("Registration error:", error);
        messageBox.style.color = "var(--danger-red)";
        messageBox.innerText = "Connection error with server.";
    }
});
