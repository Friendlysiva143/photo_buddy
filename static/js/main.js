// Mobile Navigation Toggle

const navToggle = document.getElementById("navToggle");
const dropdownMenu = document.getElementById("dropdownMenu");

// Toggle menu when hamburger is clicked
navToggle.addEventListener("click", function (event) {
    
    event.stopPropagation(); // prevent document click from firing

    if (dropdownMenu.style.display === "flex") {
        dropdownMenu.style.display = "none";
    } else {
        dropdownMenu.style.display = "flex";
    }

});

// Close menu when clicking outside
document.addEventListener("click", function (event) {

    if (!navToggle.contains(event.target) && !dropdownMenu.contains(event.target)) {
        dropdownMenu.style.display = "none";
    }

});