from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import HttpResponse
from django.urls import reverse
from django.shortcuts import get_object_or_404, redirect, render

from yatube.settings import POSTS_PER_PAGE
from .forms import PostForm, CommentForm
from .models import Comment, Follow, Group, Post, User


def index(request):
    """Provides rendering the main page."""
    title = 'Последние обновления на сайте'
    post_list = Post.objects.all()
    page_obj = get_paginator_page_obj(request, post_list, POSTS_PER_PAGE)
    context = {'title': title, 'page_obj': page_obj, 'index_nav_button': True}
    return render(request, 'posts/index.html', context)


def group(request):
    """Provides rendering the list of groups page."""
    return HttpResponse('There will be a list of groups')


def group_posts(request, sl):
    """Provides rendering group pages."""
    group = get_object_or_404(Group, slug=sl)
    posts = group.posts.all()[:10]
    post_list = group.posts.all()
    page_obj = get_paginator_page_obj(request, post_list, POSTS_PER_PAGE)
    title = f'Записи сообщества {group}'
    context = {'group': group,
               'posts': posts, 'title': title, 'page_obj': page_obj}
    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    """Provides rendering profile pages."""
    author = get_object_or_404(User, username=username)
    can_follow, following = False, False

    if request.user.is_authenticated:
        user = get_object_or_404(User, username=request.user)
        if author.id != user.id:
            can_follow = True
        if Follow.objects.filter(author=author.id, user=user.id).exists():
            following = True

    post_list = Post.objects.filter(author_id=author.id)
    page_obj = get_paginator_page_obj(request, post_list, POSTS_PER_PAGE)
    context = {'author': author, 'page_obj': page_obj,
               'following': following, 'can_follow': can_follow}
    return render(request, 'posts/profile.html', context)


def post_detail(request, id):
    """Provides rendering post detail pages."""
    post = Post.objects.get(pk=id)
    user = User.objects.get(pk=post.author_id)
    count = Post.objects.filter(author_id=post.author_id).count()
    comments = Comment.objects.filter(post_id=post.id)  # post.comments.all()
    comment_form = CommentForm(request.POST or None)
    context = {
        'post': post, 'user': user, 'count': count,
        'comments': comments, 'comment_form': comment_form,
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    """Provides rendering post creating page."""
    title = 'Новый пост'
    template = 'posts/create_post.html'
    form = PostForm(request.POST or None,
                    files=request.FILES or None,)

    if request.method == 'POST' and form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect('posts:profile', username=request.user)

    context = {'form': form, 'title': title}
    return render(request, template, context)


@login_required
def post_edit(request, id):
    """Provides rendering post editing page."""
    title = 'Редактируем пост'
    template = 'posts/create_post.html'
    post = Post.objects.get(pk=id)
    if post.author != request.user:
        return redirect('posts:post_detail', id=id)

    if request.method == 'POST':
        form = PostForm(request.POST,
                        files=request.FILES or None, instance=post)
        if form.is_valid():
            form.save()
            return redirect('posts:post_detail', id=post.id)
        context = {'form': form, 'title': title, 'is_edit': True}
        return render(request, template, context)

    form = PostForm(instance=post)
    context = {'form': form, 'title': title, 'is_edit': True}
    return render(request, template, context)


@login_required
def add_comment(request, post_id):
    """Provides rendering comment creating page."""
    post = Post.objects.get(pk=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', id=post_id)


@login_required
def follow_index(request):
    """Provides rendering the main page with subscribed authors."""
    title = 'Последние обновления ленты подписок.'
    user = request.user
    following_authors = Follow.objects.filter(user__pk=user.pk)
    following_authors = [following.author for following in following_authors]
    post_list = Post.objects.filter(author__in=following_authors)
    page_obj = get_paginator_page_obj(request, post_list, POSTS_PER_PAGE)
    context = {'title': title, 'page_obj': page_obj, 'follow_nav_button': True}
    return render(request, 'posts/follow.html', context)


@login_required
def profile_follow(request, username):
    """Makes subscription on the chosen author."""
    author = User.objects.get(username=username)
    user = User.objects.get(username=request.user)
    # дважды не подпишешься \ сам на себя не подпишешься
    if (Follow.objects.filter(author=author.id, user=user.id).exists() or 
            author.id == user.id):
        return redirect(
            to=reverse('posts:profile', kwargs={'username': username}),)
    Follow.objects.create(author=author, user=user)
    return redirect(to=reverse('posts:profile', kwargs={'username': username}))


@login_required
def profile_unfollow(request, username):
    """Deletes subscription on the chosen author."""
    author = User.objects.get(username=username)
    user = User.objects.get(username=request.user)
    instance = Follow.objects.filter(author__id=author.id, user__id=user.id)
    instance.delete()
    return redirect(to=reverse('posts:profile', kwargs={'username': username}))


def get_paginator_page_obj(request, all_obj, obj_per_page):
    """Takes a list of objects, returns a paged list of objects."""
    paginator = Paginator(all_obj, obj_per_page)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return page_obj
