function togglePassword(inputId, button) {
    const passwordInput = document.getElementById(inputId);

    if (passwordInput.type === "password") {
        passwordInput.type = "text";
        button.textContent = "Hide";
    } else {
        passwordInput.type = "password";
        button.textContent = "Show";
    }
}

// Remember student email

document.addEventListener("DOMContentLoaded", function () {

    const emailInput = document.getElementById("email");
    const rememberCheckbox = document.getElementById("remember_email");

    if (!emailInput || !rememberCheckbox) {
        return;
    }

    const savedEmail = localStorage.getItem("ecoCampusEmail");

    if (savedEmail) {
        emailInput.value = savedEmail;
        rememberCheckbox.checked = true;
    }

    emailInput.form.addEventListener("submit", function () {

        if (rememberCheckbox.checked) {
            localStorage.setItem("ecoCampusEmail", emailInput.value);
        } else {
            localStorage.removeItem("ecoCampusEmail");
        }

    });

});