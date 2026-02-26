// VehicleVault Main JavaScript
// Professional UI interactions

console.log("🚗 VehicleVault Loaded Successfully");


// ================================
// Navbar scroll effect
// ================================

window.addEventListener("scroll", function () {

    const navbar = document.querySelector(".navbar");

    if (navbar) {

        if (window.scrollY > 50) {

            navbar.classList.add("shadow-lg");
            navbar.style.transition = "0.3s";

        } else {

            navbar.classList.remove("shadow-lg");

        }
    }
});


// ================================
// Delete confirmation popup
// ================================

function confirmDelete(itemName) {

    return confirm(`⚠️ Are you sure you want to delete "${itemName}" ?`);

}


// Usage in HTML:
// onclick="return confirmDelete('Vehicle Name')"


// ================================
// Auto hide alerts after 4 seconds
// ================================

setTimeout(function () {

    let alerts = document.querySelectorAll(".alert");

    alerts.forEach(function (alert) {

        alert.style.transition = "0.5s";
        alert.style.opacity = "0";

        setTimeout(() => alert.remove(), 500);

    });

}, 4000);


// ================================
// Button loading effect
// ================================

document.querySelectorAll(".btn").forEach(button => {

    button.addEventListener("click", function () {

        if (this.classList.contains("no-loading")) return;

        let originalText = this.innerHTML;

        this.innerHTML = "⏳ Loading...";
        this.disabled = true;

        setTimeout(() => {

            this.innerHTML = originalText;
            this.disabled = false;

        }, 1500);

    });

});


// ================================
// Form validation
// ================================

document.querySelectorAll("form").forEach(form => {

    form.addEventListener("submit", function (e) {

        let inputs = form.querySelectorAll("input[required]");

        let valid = true;

        inputs.forEach(input => {

            if (input.value.trim() === "") {

                input.style.border = "2px solid red";
                valid = false;

            } else {

                input.style.border = "2px solid green";

            }

        });

        if (!valid) {

            e.preventDefault();

            alert("⚠️ Please fill all required fields");

        }

    });

});


// ================================
// Smooth page animation
// ================================

document.addEventListener("DOMContentLoaded", function () {

    document.body.style.opacity = "0";

    setTimeout(() => {

        document.body.style.transition = "opacity 0.5s";
        document.body.style.opacity = "1";

    }, 100);

});


// ================================
// Show password toggle
// ================================

function togglePassword(fieldId) {

    const field = document.getElementById(fieldId);

    if (field.type === "password") {

        field.type = "text";

    } else {

        field.type = "password";

    }

}


// ================================
// Welcome message
// ================================

document.addEventListener("DOMContentLoaded", function () {

    console.log("Welcome to VehicleVault 🚗");

});
