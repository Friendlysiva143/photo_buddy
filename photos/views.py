from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator
from .models import Post, Like, Comment
from .forms import PostForm, CommentForm


# ==================== POST FEED VIEWS ====================

@login_required
def posts_feed(request):
    """Display feed of all posts (Instagram-style)"""
    posts = Post.objects.all().select_related('user').prefetch_related('likes', 'comments')
    
    # Pagination: 10 posts per page
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'posts': page_obj.object_list,
    }
    return render(request, 'photos/posts_feed.html', context)


# ==================== CREATE POST VIEWS ====================

@login_required
def create_post(request):
    """Create a new post"""
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.user = request.user
            post.save()
            return redirect('posts:posts_feed')
    else:
        form = PostForm()
    
    context = {
        'form': form,
        'page_title': 'Create Post',
    }
    return render(request, 'photos/create_post.html', context)


# ==================== USER PROFILE POSTS ====================

def user_posts(request, username):
    """Display all posts by a specific user"""
    user = get_object_or_404(User, username=username)
    posts = Post.objects.filter(user=user).select_related('user').prefetch_related('likes', 'comments')
    
    # Pagination
    paginator = Paginator(posts, 12)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    context = {
        'profile_user': user,
        'page_obj': page_obj,
        'posts': page_obj.object_list,
        'posts_count': posts.count(),
    }
    return render(request, 'photos/user_posts.html', context)


# ==================== POST DETAIL VIEW ====================

def post_detail(request, post_id):
    """Display a single post with comments"""
    post = get_object_or_404(Post, id=post_id)
    comments = post.comments.all().select_related('user')
    
    if request.method == 'POST' and request.user.is_authenticated:
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.user = request.user
            comment.save()
            return redirect('posts:post_detail', post_id=post.id)
    else:
        form = CommentForm()
    
    context = {
        'post': post,
        'comments': comments,
        'form': form,
        'is_liked': post.is_liked_by(request.user) if request.user.is_authenticated else False,
    }
    return render(request, 'photos/post_detail.html', context)


# ==================== LIKE/UNLIKE POSTS ====================

@login_required
@require_POST
def toggle_like(request, post_id):
    """Toggle like on a post (supports AJAX)"""
    post = get_object_or_404(Post, id=post_id)
    
    like_exists = Like.objects.filter(post=post, user=request.user).exists()
    
    if like_exists:
        Like.objects.filter(post=post, user=request.user).delete()
        liked = False
    else:
        Like.objects.create(post=post, user=request.user)
        liked = True
    
    # Return JSON for AJAX requests
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'liked': liked,
            'likes_count': post.likes_count,
        })
    
    # Redirect for regular form submission
    return redirect('posts:post_detail', post_id=post.id)


# ==================== EDIT/DELETE POSTS ====================

@login_required
def edit_post(request, post_id):
    """Edit an existing post"""
    post = get_object_or_404(Post, id=post_id)
    
    # Check if user owns the post
    if post.user != request.user:
        return redirect('posts:posts_feed')
    
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
            return redirect('posts:post_detail', post_id=post.id)
    else:
        form = PostForm(instance=post)
    
    context = {
        'form': form,
        'post': post,
        'page_title': 'Edit Post',
    }
    return render(request, 'photos/edit_post.html', context)


@login_required
@require_POST
def delete_post(request, post_id):
    """Delete a post"""
    post = get_object_or_404(Post, id=post_id)
    
    # Check if user owns the post
    if post.user != request.user:
        return redirect('posts:posts_feed')
    
    post.delete()
    return redirect('posts:user_posts', username=request.user.username)


# ==================== DELETE COMMENT ====================

@login_required
@require_POST
def delete_comment(request, comment_id):
    """Delete a comment"""
    comment = get_object_or_404(Comment, id=comment_id)
    post_id = comment.post.id
    
    # Check if user owns the comment
    if comment.user != request.user:
        return redirect('posts:post_detail', post_id=post_id)
    
    comment.delete()
    return redirect('posts:post_detail', post_id=post_id)