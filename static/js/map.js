// static/js/map.js

document.addEventListener("DOMContentLoaded", function () {
    // Set Hyderabad as initial map center
    var defaultLat = 17.385;
    var defaultLng = 78.486;
    var map = L.map('map').setView([defaultLat, defaultLng], 14);

    // OpenStreetMap tile layer
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; OpenStreetMap contributors'
    }).addTo(map);

    // Try to get user's geolocation
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(function (position) {
            var userLat = position.coords.latitude;
            var userLng = position.coords.longitude;

            // Set map to user's location
            map.setView([userLat, userLng], 16);

            // Add marker for user
            var userMarker = L.marker([userLat, userLng])
                .addTo(map)
                .bindPopup("You are here!")
                .openPopup();

            // Here: fetch and display other nearby users (mockup for now)
            // In real app, use AJAX to get nearby checked-in users
            let exampleUsers = [
                { username: "Rahul", lat: userLat + 0.001, lng: userLng + 0.002, rating: 4.8 },
                { username: "Aarti", lat: userLat - 0.002, lng: userLng + 0.003, rating: 4.6 }
            ];
            exampleUsers.forEach(u => {
                let buddyMarker = L.marker([u.lat, u.lng])
                    .addTo(map)
                    .bindPopup(
                        `<strong>${u.username}</strong><br>Rating: ${u.rating} ★<br>
                        <a href='/matches/request?user=${u.username}' class='btn btn-sm btn-primary'>Send Match Request</a>`
                    );
            });

            // List view below the map
            let userListEl = document.getElementById('nearby-users');
            userListEl.innerHTML = '';
            exampleUsers.forEach(u => {
                let li = document.createElement('li');
                li.innerHTML = `
                    <div style="display:flex;align-items:center;justify-content:space-between;padding:8px 0;">
                        <span>
                            <i class="fas fa-user"></i>
                            <strong>${u.username}</strong>
                        </span>
                        <span>
                            Rating: ${u.rating} ★
                            <a href='/matches/request?user=${u.username}' class='btn btn-primary btn-sm' style='margin-left:8px;'>Request</a>
                        </span>
                    </div>
                `;
                userListEl.appendChild(li);
            });
        }, function error() {
            alert("Cannot detect your location. Map will show Hyderabad by default.");
        });
    } else {
        alert("Geolocation is not supported by your browser.");
    }
});
