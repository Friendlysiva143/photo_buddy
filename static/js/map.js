document.addEventListener("DOMContentLoaded", function () {
    const defaultLat = 17.385;
    const defaultLng = 78.486;
    const map = L.map('map').setView([defaultLat, defaultLng], 14);

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; OpenStreetMap contributors'
    }).addTo(map);

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

    // AJAX request for match (normal users)
    window.sendMatchRequest = function(username, btnElement = null) {
        if (btnElement) {
            btnElement.disabled = true;
            btnElement.innerText = "Sending...";
        }
        fetch('/matches/send-request/', {
            method: 'POST',
            credentials: "same-origin",
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
                'X-CSRFToken': csrftoken
            },
            body: `username=${encodeURIComponent(username)}`
        })
        .then(res => res.json().then(data => { return {ok: res.ok, status: res.status, data: data}; }))
        .then(resp => {
            let data = resp.data;
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
                alert(`❌ ${data.message || "Something went wrong."}`);
                if (btnElement) {
                    btnElement.disabled = false;
                    btnElement.innerText = "Request";
                }
            }
        })
        .catch(err => {
            console.error("Match request failed:", err);
            alert("❌ Something went wrong. Please try again.");
            if (btnElement) {
                btnElement.disabled = false;
                btnElement.innerText = "Request";
            }
        });
    };

    // AJAX request for cameraman
    window.requestCameraman = function(username, btnElement = null) {
        if (btnElement) {
            btnElement.disabled = true;
            btnElement.innerText = "Requesting...";
        }
        fetch('/request-cameraman/', {
            method: 'POST',
            credentials: "same-origin",
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
                'X-CSRFToken': csrftoken
            },
            body: `username=${encodeURIComponent(username)}`
        })
        .then(res => res.json().then(data => { return {ok: res.ok, status: res.status, data: data}; }))
        .then(resp => {
            let data = resp.data;
            if (data.status === 'sent') {
                alert(`✅ Cameraman request sent to ${username}`);
                if (btnElement) {
                    btnElement.innerText = "Requested ✔";
                    btnElement.classList.remove("btn-danger");
                    btnElement.classList.add("btn-success");
                }
            } else if (data.status === 'user_not_found') {
                alert(`❌ Cameraman not found: ${username}`);
                if (btnElement) btnElement.disabled = false;
            } else {
                alert(`❌ ${data.message || "Something went wrong."}`);
                if (btnElement) {
                    btnElement.disabled = false;
                    btnElement.innerText = "Request Cameraman";
                }
            }
        })
        .catch(err => {
            console.error("Cameraman request failed:", err);
            alert("❌ Something went wrong. Please try again.");
            if (btnElement) {
                btnElement.disabled = false;
                btnElement.innerText = "Request Cameraman";
            }
        });
    };

    function initMap(userLat = defaultLat, userLng = defaultLng) {
        map.setView([userLat, userLng], 16);

        L.marker([userLat, userLng])
            .addTo(map)
            .bindPopup("You are here!")
            .openPopup();

        fetch('/locations/update-location/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrftoken
            },
            body: JSON.stringify({latitude: userLat, longitude: userLng})
        });

        fetch('/locations/nearby-users-json/')
            .then(res => res.json())
            .then(users => {
                const userListEl = document.getElementById('nearby-users');
                if (userListEl) userListEl.innerHTML = '';
                users.forEach(u => {
                    let markerIcon = L.icon({
                        iconUrl: u.is_cameraman ? '/static/images/cameraman-marker.png' : '/static/images/user-marker.png',
                        iconSize: [32, 32],
                        iconAnchor: [16, 32],
                        popupAnchor: [0, -32]
                    });
                    const marker = L.marker([u.lat, u.lng], {icon: markerIcon}).addTo(map);
                    let popupHtml = `<strong>${u.username}</strong><br>`;
                    if (u.is_cameraman) {
                        popupHtml += `<span style="color:red;">Professional Cameraman</span><br>`;
                        popupHtml += `<button class="btn btn-sm btn-danger" onclick="requestCameraman('${u.username}', this)">Request Cameraman</button>`;
                    } else {
                        popupHtml += `<button class="btn btn-sm btn-primary" onclick="sendMatchRequest('${u.username}', this)">Request</button>`;
                    }
                    marker.bindPopup(popupHtml);

                    if (userListEl) {
                        const li = document.createElement('li');
                        li.innerHTML = `
                            <div style="display:flex;justify-content:space-between;align-items:center;padding:5px 0;">
                                <span>
                                    ${u.username}${u.is_cameraman ? ' <span style="color:red;">&#11044; Cameraman</span>' : ''}
                                </span>
                                ${
                                    u.is_cameraman
                                        ? `<button class="btn btn-sm btn-danger" onclick="requestCameraman('${u.username}', this)">Request Cameraman</button>`
                                        : `<button class="btn btn-sm btn-primary" onclick="sendMatchRequest('${u.username}', this)">Request</button>`
                                }
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
