from django.urls import path
from . import views

app_name = 'posts'

urlpatterns = [
    # ==================== POSTS FEED ====================
    path('', views.posts_feed, name='posts_feed'),

    # ==================== CREATE POST ====================
    path('create/', views.create_post, name='create_post'),

    # ==================== VIEW SINGLE POST ====================
    path('post/<int:post_id>/', views.post_detail, name='post_detail'),

    # ==================== EDIT / DELETE POST ====================
    path('post/<int:post_id>/edit/', views.edit_post, name='edit_post'),
    path('post/<int:post_id>/delete/', views.delete_post, name='delete_post'),

    # ==================== LIKE / UNLIKE ====================
    path('post/<int:post_id>/like/', views.toggle_like, name='toggle_like'),

    # ==================== COMMENTS ====================
    path('comment/<int:comment_id>/delete/', views.delete_comment, name='delete_comment'),

    # ==================== USER PROFILE POSTS ====================
    path('user/<str:username>/', views.user_posts, name='user_posts'),

    # ============================================================
    # NEW: TAG POSTS (for clickable #hashtags)
    # ============================================================
    path('tag/<str:tag>/', views.tag_posts, name='tag_posts'),

    
    path('recommended/', views.recommended_posts_view, name='recommended_posts'),


]
