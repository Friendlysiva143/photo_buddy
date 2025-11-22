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

    // Send match request function
    function sendMatchRequest(username, btnElement = null) {
    // If button passed → disable it immediately
    if (btnElement) {
        btnElement.disabled = true;
        btnElement.innerText = "Sending...";
    }

    fetch('/matches/request/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
            'X-CSRFToken': csrftoken
        },
        body: `username=${encodeURIComponent(username)}`
    })
    .then(res => res.json())
    .then(data => {
        if (data.status === "success") {
            alert("✅ Match request sent to " + username);

            if (btnElement) {
                btnElement.innerText = "Sent ✔";
                btnElement.classList.remove("btn-primary");
                btnElement.classList.add("btn-success");
            }

        } else if (data.status === "exists") {
            alert("⚠ Request already sent to " + username);

            if (btnElement) {
                btnElement.innerText = "Already Sent";
            }

        } else {
            alert("❌ " + data.message);

            if (btnElement) {
                btnElement.disabled = false;
                btnElement.innerText = "Request";
            }
        }
    })
    .catch(err => {
        console.error(err);
        alert("❌ Something went wrong.");

        if (btnElement) {
            btnElement.disabled = false;
            btnElement.innerText = "Request";
        }
    });
    }



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
                    let userListEl = document.getElementById('nearby-users');
                    userListEl.innerHTML = '';

                    users.forEach(u => {
                        // Add marker for each user
                        const marker = L.marker([u.lat, u.lng])
                            .addTo(map)
                            .bindPopup(
                                `<strong>${u.username}</strong><br>
                                 <button class='btn btn-sm btn-primary' onclick="sendMatchRequest('${u.username}')">Send Match Request</button>`
                            );

                        // Add list view entry
                        const li = document.createElement('li');
                        li.innerHTML = `
                            <div style="display:flex;align-items:center;justify-content:space-between;padding:8px 0;">
                                <span><i class="fas fa-user"></i> <strong>${u.username}</strong></span>
                                <span>
                                    <button class='btn btn-primary btn-sm' onclick="sendMatchRequest('${u.username}')">Request</button>
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
