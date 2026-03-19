const authMessage = document.getElementById("auth-message");

const setAuthMessage = (message, isError = false) => {
    authMessage.textContent = message;
    authMessage.classList.toggle("error-message", isError);
};

const submitAuthForm = async (event, endpoint, successMessage) => {
    event.preventDefault();
    const form = event.currentTarget;
    const formData = new FormData(form);
    const payload = Object.fromEntries(formData.entries());

    const response = await fetch(endpoint, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
    });

    if (!response.ok) {
        const data = await response.json();
        setAuthMessage(data.detail || "Authentication failed.", true);
        return;
    }

    setAuthMessage(successMessage);
    window.location.href = "/";
};

document.getElementById("login-form").addEventListener("submit", (event) => {
    submitAuthForm(event, "/api/auth/login", "Login successful. Opening your dashboard...");
});

document.getElementById("register-form").addEventListener("submit", (event) => {
    submitAuthForm(event, "/api/auth/register", "Account created. Opening your dashboard...");
});
