const navToggle = document.getElementById("navToggle");
const dropdown = document.getElementById("dropdownMenu");

// Show menu on hover
navToggle.addEventListener("mouseenter", () => {
    dropdown.style.display = "flex";
});

// Also keep it open while mouse is inside menu
dropdown.addEventListener("mouseenter", () => {
    dropdown.style.display = "flex";
});

// Hide when mouse leaves both
navToggle.addEventListener("mouseleave", () => {
    setTimeout(() => {
        if (!dropdown.matches(':hover')) {
            dropdown.style.display = "none";
        }
    }, 200);
});

dropdown.addEventListener("mouseleave", () => {
    dropdown.style.display = "none";
});
