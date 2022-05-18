from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.cache import cache_page
from django.contrib.auth.models import User

from .forms import CommentForm, PostForm
from .models import Follow, Group, Post, User
from .utils import paginator


@cache_page(15)
def index(request):
    post_list = Post.objects.select_related('author', 'group')
    context = {
        'page_obj': paginator(request, post_list),
    }
    return render(request, 'posts/index.html', context)


@login_required
def follow_index(request):
    post_list = (
        Post.objects.select_related()
        .filter(author__following__user=request.user)
    )
    context = {'page_obj': paginator(request, post_list), }
    return render(request, 'posts/follow.html', context)


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    follower = Follow.objects.filter(
        user=request.user, author=author).exists()
    if username != request.user.username and not follower:
        Follow.objects.get_or_create(
            user=request.user,
            author=author,
        )
    return redirect('posts:profile', username=username)


@login_required
def profile_unfollow(request, username):
    author = get_object_or_404(User, username=username)
    follower = Follow.objects.filter(
        user=request.user, author=author).exists()
    if author != request.user and follower:
        following = Follow.objects.get(
            user=request.user,
            author=author,
        )
        following.delete()
    return redirect('posts:profile', username=username)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    post_list = group.posts.select_related('author')
    context = {
        'page_obj': paginator(request, post_list),
        'group': group,
    }
    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    author = get_object_or_404(User, username=username)
    post_list = author.posts.select_related('group')
    count_post_author = len(post_list)
    # if request.user.is_authenticated:
    if author != request.user and request.user.is_authenticated:
        following = Follow.objects.filter(
            user=request.user, author=author).exists()
    else:
        following = False
    context = {
        'author': author,
        'page_obj': paginator(request, post_list),
        'count_post_author': count_post_author,
        'following': following,
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    page_obj = Post.objects.get(pk=post_id)
    form = CommentForm(request.POST or None,)
    # comments = Comment.objects.filter(pk=post_id)
    # comments = Comment.objects.all()
    # comments = Comment.objects.get(pk=post_id)
    # почему не так?
    comments = page_obj.comments.all()
    context = {
        'page_obj': page_obj,
        'form': form,
        'comments': comments,
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
    )
    context = {'form': form}
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect('posts:profile', username=request.user.username)
    return render(request, 'posts/create_post.html', context)


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    if request.user != post.author:
        return redirect('posts:post_detail', post_id=post_id)
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post,
    )
    if form.is_valid():
        form.save()
        return redirect('posts:post_detail', post_id=post_id)
    return render(request, 'posts/create_post.html', {'form': form})


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)
