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

    // CSRF token for POST
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
    const csrftoken = getCookie('csrftoken');

    // Try to get user's geolocation
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(function (position) {
            var userLat = position.coords.latitude;
            var userLng = position.coords.longitude;

            // Set map to user's location
            map.setView([userLat, userLng], 16);

            // Add marker for user
            L.marker([userLat, userLng])
                .addTo(map)
                .bindPopup("You are here!")
                .openPopup();

            // Send user location to backend
            fetch('/locations/update-location/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrftoken
                },
                body: JSON.stringify({latitude: userLat, longitude: userLng})
            });

            // Fetch nearby users from backend
            fetch('/locations/nearby-users-json/')
                .then(res => res.json())
                .then(users => {
                    // Clear existing nearby users list
                    let userListEl = document.getElementById('nearby-users');
                    userListEl.innerHTML = '';

                    users.forEach(u => {
                        // Add markers for each user
                        L.marker([u.lat, u.lng])
                            .addTo(map)
                            .bindPopup(
                                `<strong>${u.username}</strong><br>
                                 <a href='/matches/request?user=${u.username}' class='btn btn-sm btn-primary'>Send Match Request</a>`
                            );

                        // Add list view entry
                        let li = document.createElement('li');
                        li.innerHTML = `
                            <div style="display:flex;align-items:center;justify-content:space-between;padding:8px 0;">
                                <span><i class="fas fa-user"></i> <strong>${u.username}</strong></span>
                                <span>
                                    <a href='/matches/request?user=${u.username}' class='btn btn-primary btn-sm' style='margin-left:8px;'>Request</a>
                                </span>
                            </div>
                        `;
                        userListEl.appendChild(li);
                    });
                });

        }, function error() {
            alert("Cannot detect your location. Map will show Hyderabad by default.");
        });
    } else {
        alert("Geolocation is not supported by your browser.");
    }
});
