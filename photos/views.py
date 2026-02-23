from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
User = get_user_model()
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator
from .models import (
    Post,
    Like,
    Comment,
    PostView,
    UserPostInteraction,
    Mention
)
from .forms import PostForm, CommentForm
import re   
from django.contrib.auth import get_user_model 

# ==================== POST FEED ====================

@login_required
def posts_feed(request):
    posts = Post.objects.all().select_related('user').prefetch_related('likes', 'comments')

    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    return render(request, 'photos/posts_feed.html', {
        'page_obj': page_obj,
        'posts': page_obj.object_list,
    })


# ==================== CREATE POST ====================

@login_required
def create_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)

        if form.is_valid():
            post = form.save(commit=False)
            post.user = request.user
            post.save()
            form.save_m2m()

            # =========================
            # NEW: Extract @mentions
            # =========================
            caption = post.caption

            usernames = re.findall(r'@(\w+)', caption)

            User = get_user_model()

            for uname in usernames:
                try:
                    mentioned_user = User.objects.get(username=uname)
                    Mention.objects.create(
                        post=post,
                        user=mentioned_user
                    )
                except User.DoesNotExist:
                    pass

            return redirect('posts:posts_feed')

    else:
        form = PostForm()

    return render(request, 'photos/create_post.html', {
        'form': form,
        'page_title': 'Create Post',
    })



# ==================== USER POSTS ====================

def user_posts(request, username):
    user = get_object_or_404(User, username=username)
    posts = Post.objects.filter(user=user).select_related('user').prefetch_related('likes', 'comments')

    paginator = Paginator(posts, 12)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    return render(request, 'photos/user_posts.html', {
        'profile_user': user,
        'page_obj': page_obj,
        'posts': page_obj.object_list,
        'posts_count': posts.count(),
    })


# ==================== POST DETAIL ====================

def post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    comments = post.comments.all().select_related('user')

    # 🔹 LOG VIEW
    if request.user.is_authenticated:
        PostView.objects.get_or_create(
            post=post,
            user=request.user
        )
        UserPostInteraction.objects.create(
            user=request.user,
            post=post,
            interaction_type='view',
            weight=1.0
        )

    if request.method == 'POST' and request.user.is_authenticated:
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.user = request.user
            comment.save()

            # 🔹 LOG COMMENT
            UserPostInteraction.objects.create(
                user=request.user,
                post=post,
                interaction_type='comment',
                weight=5.0
            )

            return redirect('posts:post_detail', post_id=post.id)
    else:
        form = CommentForm()

    return render(request, 'photos/post_detail.html', {
        'post': post,
        'comments': comments,
        'form': form,
        'is_liked': post.is_liked_by(request.user) if request.user.is_authenticated else False,
    })


# ==================== LIKE / UNLIKE ====================

@login_required
@require_POST
def toggle_like(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    if Like.objects.filter(post=post, user=request.user).exists():
        Like.objects.filter(post=post, user=request.user).delete()
        liked = False
    else:
        Like.objects.create(post=post, user=request.user)
        liked = True

        # 🔹 LOG LIKE
        UserPostInteraction.objects.create(
            user=request.user,
            post=post,
            interaction_type='like',
            weight=3.0
        )

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'liked': liked,
            'likes_count': post.likes_count,
        })

    return redirect('posts:post_detail', post_id=post.id)


# ==================== EDIT POST ====================

@login_required
def edit_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    if post.user != request.user:
        return redirect('posts:posts_feed')

    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
            return redirect('posts:post_detail', post_id=post.id)
    else:
        form = PostForm(instance=post)

    return render(request, 'photos/edit_post.html', {
        'form': form,
        'post': post,
        'page_title': 'Edit Post',
    })


# ==================== DELETE POST ====================

@login_required
@require_POST
def delete_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    if post.user != request.user:
        return redirect('posts:posts_feed')

    post.delete()
    return redirect('posts:user_posts', username=request.user.username)


# ==================== DELETE COMMENT ====================

@login_required
@require_POST
def delete_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    post_id = comment.post.id

    if comment.user != request.user:
        return redirect('posts:post_detail', post_id=post_id)

    comment.delete()
    return redirect('posts:post_detail', post_id=post_id)

def tag_posts(request, tag):
    posts = Post.objects.filter(
        caption__icontains=f'#{tag}'
    ).select_related('user')

    return render(request, 'photos/posts_feed.html', {
        'posts': posts,
        'page_obj': posts
    })

#from .recommendation import collaborative_recommend

def recommended_posts_view(request):
    """if request.user.is_authenticated:
        recommended_ids = collaborative_recommend(request.user.id, top_n=10)
        posts = Post.objects.filter(id__in=recommended_ids)
    else:
        # fallback for anonymous users → popular posts
        posts = Post.objects.all().order_by('-created_at')[:10]

    return render(request, 'photos/recommended.html', {'posts': posts})"""
    return render(request, 'photos/recommended.html', {'posts': []})