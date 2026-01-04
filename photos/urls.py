from django.urls import path
from . import views

app_name = 'posts'

urlpatterns = [
    # Posts Feed
    path('', views.posts_feed, name='posts_feed'),
    
    # Create Post
    path('create/', views.create_post, name='create_post'),
    
    # View Single Post
    path('post/<int:post_id>/', views.post_detail, name='post_detail'),
    
    # Edit/Delete Posts
    path('post/<int:post_id>/edit/', views.edit_post, name='edit_post'),
    path('post/<int:post_id>/delete/', views.delete_post, name='delete_post'),
    
    # Like/Unlike
    path('post/<int:post_id>/like/', views.toggle_like, name='toggle_like'),
    
    # Comments
    path('comment/<int:comment_id>/delete/', views.delete_comment, name='delete_comment'),
    
    # User Profile Posts
    path('user/<str:username>/', views.user_posts, name='user_posts'),
]