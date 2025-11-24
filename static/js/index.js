
document.addEventListener('DOMContentLoaded', function() {
    let index = 0;
    let slides = document.querySelectorAll('.carousel-img');
    function showSlide(idx) {
        slides.forEach((img, i) => {
            img.style.display = (i === idx) ? 'block' : 'none';
        });
    }
    setInterval(function() {
        index = (index + 1) % slides.length;
        showSlide(index);
    }, 3000); // change image every 3 seconds
    showSlide(index); // Show first slide on load
});
