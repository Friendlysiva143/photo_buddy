// static/js/map.js

document.addEventListener("DOMContentLoaded", function () {
    // Set default map center (Hyderabad)
    const defaultLat = 17.385;
    const defaultLng = 78.486;
    const map = L.map('map').setView([defaultLat, defaultLng], 14);

    // OpenStreetMap tiles
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; OpenStreetMap contributors'
    }).addTo(map);

    // CSRF token
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            cookies.forEach(cookie => {
                cookie = cookie.trim();
                if (cookie.startsWith(name + '=')) {
                    cookieValue = decodeURIComponent(cookie.slice(name.length + 1));
                }
            });
        }
        return cookieValue;
    }
    const csrftoken = getCookie('csrftoken');

    // Global function to send match request
    window.sendMatchRequest = function(username, btnElement = null) {
        if (btnElement) {
            btnElement.disabled = true;
            btnElement.innerText = "Sending...";
        }

        fetch('/matches/send-request/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
                'X-CSRFToken': csrftoken
            },
            body: `username=${encodeURIComponent(username)}`
        })
        .then(res => res.json())
        .then(data => {
            if (data.status === 'sent') {
                alert(`✅ Match request sent to ${username}`);
                if (btnElement) {
                    btnElement.innerText = "Sent ✔";
                    btnElement.classList.remove("btn-primary");
                    btnElement.classList.add("btn-success");
                }
            } else if (data.status === 'already_sent') {
                alert(`⚠ Request already sent to ${username}`);
                if (btnElement) btnElement.innerText = "Already Sent";
            } else if (data.status === 'user_not_found') {
                alert(`❌ User not found: ${username}`);
                if (btnElement) btnElement.disabled = false;
            } else {
                alert(`❌ Something went wrong.`);
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

    // Detect user's location
    function initMap(userLat = defaultLat, userLng = defaultLng) {
        map.setView([userLat, userLng], 16);

        // Add marker for current user
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

        // Fetch nearby users
        fetch('/locations/nearby-users-json/')
            .then(res => res.json())
            .then(users => {
                const userListEl = document.getElementById('nearby-users');
                if (userListEl) userListEl.innerHTML = '';

                users.forEach(u => {
                    // Map marker
                    const marker = L.marker([u.lat, u.lng]).addTo(map);
                    marker.bindPopup(
                        `<strong>${u.username}</strong><br>
                         <button class="btn btn-sm btn-primary" onclick="sendMatchRequest('${u.username}', this)">Send Match Request</button>`
                    );

                    // Sidebar / list
                    if (userListEl) {
                        const li = document.createElement('li');
                        li.innerHTML = `
                            <div style="display:flex;justify-content:space-between;align-items:center;padding:5px 0;">
                                <span>${u.username}</span>
                                <button class="btn btn-sm btn-primary" onclick="sendMatchRequest('${u.username}', this)">Request</button>
                            </div>
                        `;
                        userListEl.appendChild(li);
                    }
                });
            });
    }

    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(
            pos => initMap(pos.coords.latitude, pos.coords.longitude),
            err => {
                alert("Cannot detect your location. Showing default location (Hyderabad).");
                initMap();
            }
        );
    } else {
        alert("Geolocation not supported. Showing default location (Hyderabad).");
        initMap();
    }
});
