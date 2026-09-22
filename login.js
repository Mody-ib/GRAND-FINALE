const API_URL = "http://127.0.0.1:8000/api";

document.getElementById("login-form").addEventListener("submit", async (e) => {
    e.preventDefault();

    const email = document.getElementById("login-email").value;
    const password = document.getElementById("login-password").value;
    const messageBox = document.getElementById("login-message");

    messageBox.style.color = "var(--text-muted)";
    messageBox.innerText = "Signing in...";

    try {
        const response = await fetch(`${API_URL}/login`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ email, password })
        });

        const data = await response.json();

        if (response.ok) {
            messageBox.style.color = "var(--primary-emerald)";
            messageBox.innerText = "Login successful! Redirecting...";
            
            // حفظ بيانات الجلسة/التوكن وتوجيه المستخدم للصفحة الرئيسية
            if (data.token) {
                localStorage.setItem("authToken", data.token);
            }
            setTimeout(() => {
                window.location.href = "index.html";
            }, 1000);
        } else {
            messageBox.style.color = "var(--danger-red)";
            messageBox.innerText = data.detail || "Invalid email or password.";
        }
    } catch (error) {
        console.error("Login error:", error);
        messageBox.style.color = "var(--danger-red)";
        messageBox.innerText = "Connection error with server.";
    }
});