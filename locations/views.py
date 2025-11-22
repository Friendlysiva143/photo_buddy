from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import UserLocation
import math
import json
from django.views.decorators.csrf import csrf_exempt

# Haversine distance
def distance(lat1, lon1, lat2, lon2):
    R = 6371000
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    return R * c

@login_required
def nearby_users(request):
    user_loc = UserLocation.objects.filter(user=request.user).first()
    if not user_loc:
        return JsonResponse([], safe=False)

    nearby = []
    for loc in UserLocation.objects.exclude(user=request.user):
        if distance(user_loc.latitude, user_loc.longitude, loc.latitude, loc.longitude) <= 500:
            nearby.append({
                'username': loc.user.username,
                'lat': loc.latitude,
                'lng': loc.longitude,
            })
    return JsonResponse(nearby, safe=False)

@csrf_exempt
@login_required
def update_location(request):
    if request.method == "POST":
        data = json.loads(request.body)
        lat = data.get('latitude')
        lng = data.get('longitude')

        UserLocation.objects.update_or_create(
            user=request.user,
            defaults={'latitude': lat, 'longitude': lng}
        )
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'}, status=400)
