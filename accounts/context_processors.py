from .models import CustomUser

def navbar_profile(request):
    user_id = request.session.get('user_id')
    profile_pic_url = None
    username = None
    if user_id:
        try:
            user = CustomUser.objects.get(id=user_id)
            if user.profile_picture:
                profile_pic_url = user.profile_picture.url
            username = user.username
        except CustomUser.DoesNotExist:
            pass
    return {
        'navbar_profile_pic': profile_pic_url,
        'navbar_username': username,
    }
