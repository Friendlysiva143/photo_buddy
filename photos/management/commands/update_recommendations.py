from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from photos.models import UserPostInteraction, Post, UserRecommendation
from photos.recommendation import collaborative_recommend

class Command(BaseCommand):
    help = 'Precompute top recommendations for all users'

    def handle(self, *args, **kwargs):
        print("Starting recommendation update...")

        User = get_user_model()  # ✅ FIXED
        users = User.objects.all()

        for user in users:
            recommended_ids = collaborative_recommend(user.id, top_n=10)
            # Clear old recommendations
            UserRecommendation.objects.filter(user=user).delete()
            # Save new recommendations
            for post_id in recommended_ids:
                UserRecommendation.objects.create(user=user, post_id=post_id)

            print(f"Recommendations updated for {user.username}")

        print("Recommendation update complete.")