from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from yatube.settings import POSTS_ON_THE_PAGES

from .models import Follow, Group, Post, User
from posts.forms import CommentForm, PostForm


def index(request):
    posts = Post.objects.all()
    paginator = Paginator(posts, POSTS_ON_THE_PAGES)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'posts/index.html', context)


def group_posts(request, SlugField):
    group = get_object_or_404(Group, slug=SlugField)
    posts = group.groups4all.all()
    paginator = Paginator(posts, POSTS_ON_THE_PAGES)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'group': group,
        'page_obj': page_obj,
    }
    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    following = False
    if request.user.is_authenticated:
        author = User.objects.get(username=username)
        follow = Follow.objects.filter(user=request.user, author=author)
        if len(follow) != 0:
            following = True
    user = get_object_or_404(User, username=username)
    posts = user.posts.all()
    paginator = Paginator(posts, POSTS_ON_THE_PAGES)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'username': user,
        'page_obj': page_obj,
        'following': following
    }
    return render(request, 'posts/profile.html', context)


@login_required
def add_comment(request, post_id):
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = get_object_or_404(Post, id=post_id)
        comment.save()
    return redirect(reverse('post:post_detail', args=[post_id]))


def post_detail(request, post_id):
    is_edit = False
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST or None,)
    if request.method == 'POST':
        if form.is_valid():
            comment = form.save(commit=False)
            comment.author = request.user
            comment.post = request.post
            comment.save()
            return redirect(reverse('post:post_detail', args=[post_id]))
        else:
            return render(request, reverse('post:post_detail', args=[post_id]),
                          {'form': form, })

    if post.author == request.user:
        is_edit = True
    context = {
        'post': post,
        'form': form,
        'is_edit': is_edit,
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    is_edit = False
    form = PostForm(request.POST or None,
                    files=request.FILES or None,)
    if request.method == 'POST':
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect(reverse('post:profile',
                            args=[request.user.username]))
        else:
            return render(request, 'posts/create_post.html',
                          {'form': form, 'is_edit': is_edit})

    form = {'form': form, 'is_edit': is_edit}
    return render(request, 'posts/create_post.html', form)


@login_required
def post_edit(request, post_id):
    post = Post.objects.get(pk=post_id)
    form = PostForm(request.POST or None,
                    files=request.FILES or None,
                    instance=post)
    if post.author == request.user:
        is_edit = True
        if request.method == 'POST':
            if form.is_valid():
                form.save()
                return redirect(reverse('post:post_detail', args=[post_id]))
            else:
                return render(request, 'posts/create_post.html',
                              {'form': form, 'is_edit': is_edit})
        form = {'form': form, 'is_edit': is_edit}
        return render(request, 'posts/create_post.html', form)
    else:
        return redirect(reverse('post:post_detail', args=[post_id]))


@login_required
def follow_index(request):
    follow = Follow.objects.filter(user=request.user)
    follow_list = follow.values_list('author')
    posts = Post.objects.filter(author__in=follow_list)
    paginator = Paginator(posts, POSTS_ON_THE_PAGES)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {'page_obj': page_obj}
    return render(request, 'posts/follow.html', context)


@login_required
def profile_follow(request, username):
    author = User.objects.get(username=username)
    if (request.user == author
            or request.user.follower.filter(author=author).exists()):
        return redirect(reverse('post:profile', args=[username]))

    Follow.objects.create(user=request.user, author=author)
    return redirect(reverse('post:profile', args=[username]))


@login_required
def profile_unfollow(request, username):
    author = User.objects.get(username=username)
    follow = Follow.objects.get(user=request.user, author=author)
    follow.delete()
    return redirect(reverse('post:profile', args=[username]))
