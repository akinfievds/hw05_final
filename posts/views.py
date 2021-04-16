from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from .forms import CommentForm, PostForm
from .models import Follow, Group, Post, User
from .settings import PAGE_POSTS_COUNT


def index(request):
    posts = Post.objects.all()
    paginator = Paginator(posts, PAGE_POSTS_COUNT)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    context = {'page': page}
    return render(request, 'index.html', context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.all()
    paginator = Paginator(posts, PAGE_POSTS_COUNT)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    context = {'group': group, 'page': page}
    return render(request, 'group.html', context)


@login_required
def new_post(request):
    form = PostForm(request.POST or None, files=request.FILES or None)
    if not form.is_valid():
        return render(request, 'new_post.html', {'form': form})
    new_post = form.save(commit=False)
    new_post.author = request.user
    new_post.save()
    return redirect('index')


def profile(request, username):
    author = get_object_or_404(User, username=username)
    posts = author.posts.all()
    is_author = False
    if author == request.user:
        is_author = True
    paginator = Paginator(posts, PAGE_POSTS_COUNT)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    following = (
        request.user.is_authenticated
        and Follow.objects.filter(user=request.user, author=author)
    )
    context = {
        'author': author,
        'page': page,
        'following': following,
        'is_author': is_author
    }
    return render(request, 'profile.html', context)


def post_view(request, username, post_id):
    post = get_object_or_404(Post, author__username=username, id=post_id)
    is_author = False
    if post.author == request.user:
        is_author = True
    form = CommentForm(request.POST or None)
    if form.is_valid():
        new_comment = form.save(commit=False)
        new_comment.author = request.user
        new_comment.post = post
        new_comment.save()
        return redirect('post', username=username, post_id=post.id)
    comments = post.comments.all()
    is_post = True
    following = (
        request.user.is_authenticated
        and Follow.objects.filter(user=request.user, author=post.author)
    )
    context = {
        'post': post,
        'form': form,
        'following': following,
        'comments': comments,
        'is_post': is_post,
        'is_author': is_author,
    }
    return render(request, 'post.html', context)


@login_required
def add_comment(request, username, post_id):
    post = get_object_or_404(Post, author__username=username, id=post_id)
    form = CommentForm(request.POST)
    if form.is_valid():
        new_comment = form.save(commit=False)
        new_comment.author = request.user
        new_comment.post = post
        new_comment.save()
    return redirect('post', username=username, post_id=post_id)


@login_required
def post_edit(request, username, post_id):
    if username != request.user.username:
        return redirect('post', username=username, post_id=post_id)
    post = get_object_or_404(Post, author=request.user, id=post_id)
    form = PostForm(request.POST or None, files=request.FILES or None,
                    instance=post)
    if not form.is_valid():
        context = {'form': form, 'post': post}
        return render(request, 'new_post.html', context)
    form.save()
    return redirect('post', username=username, post_id=post_id)


def page_not_found(request, exception):
    return render(
        request,
        'misc/404.html',
        {'path': request.path}, status=404)


def server_error(request):
    return render(
        request,
        'misc/500.html', status=500)


@login_required
def follow_index(request):
    posts = Post.objects.filter(author__following__user=request.user)
    paginator = Paginator(posts, PAGE_POSTS_COUNT)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    context = {'page': page, 'posts': posts}
    return render(request, 'follow.html', context)


@login_required
def profile_follow(request, username):
    follow_user = get_object_or_404(User, username=username)
    if follow_user != request.user:
        Follow.objects.get_or_create(user=request.user, author=follow_user)
    return redirect('profile', username=username)


@login_required
def profile_unfollow(request, username):
    unfollow_user = get_object_or_404(User, username=username)
    get_object_or_404(
        Follow,
        user=request.user,
        author=unfollow_user
    ).delete()
    return redirect('profile', username=username)
