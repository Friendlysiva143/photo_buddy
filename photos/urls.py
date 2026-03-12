from django.urls import path
from . import views

app_name = 'posts'

urlpatterns = [
    path('', views.posts_feed, name='posts_feed'),
    path('create/', views.create_post, name='create_post'),
    path('post/<int:post_id>/', views.post_detail, name='post_detail'),
    path('post/<int:post_id>/edit/', views.edit_post, name='edit_post'),
    path('post/<int:post_id>/delete/', views.delete_post, name='delete_post'),
    path('post/<int:post_id>/like/', views.toggle_like, name='toggle_like'),

    # NEW AJAX COMMENT URL
    path('post/<int:post_id>/comment/ajax/', views.add_comment_ajax, name='add_comment_ajax'),

    path('comment/<int:comment_id>/delete/', views.delete_comment, name='delete_comment'),
    path('user/<str:username>/', views.user_posts, name='user_posts'),
    path('tag/<str:tag>/', views.tag_posts, name='tag_posts'),
    path('recommended/', views.recommended_posts_view, name='recommended_posts'),
]