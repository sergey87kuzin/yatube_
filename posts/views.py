from http import HTTPStatus

from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from .forms import AvatarForm, CommentForm, PostForm
from .models import Avatar, Follow, Group, Post, User


def index(request):
    post_list = Post.objects.all()
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page_count = paginator.per_page
    page = paginator.get_page(page_number)
    return render(request, 'index.html', {'page': page,
                                          'count': page_count,
                                          'changes': 'index', })


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts_list = group.posts.all()
    paginator = Paginator(posts_list, 10)
    page_number = request.GET.get('page')
    page_count = paginator.per_page
    page = paginator.get_page(page_number)
    return render(request, 'group.html', {'group': group,
                                          'page': page,
                                          'count': page_count,
                                          'changes': 'index', })


@login_required
def new_post(request):
    form = PostForm(request.POST or None, files=request.FILES or None)
    if form.is_valid():
        form.instance.author = request.user
        form.save()
        return redirect('index')
    return render(request, 'new.html', {'form': form,
                                        'changes': 'new', })


def profile(request, username):
    user = get_object_or_404(User, username=username)
    following = False
    if request.user.is_authenticated:
        following = Follow.objects.filter(
            author=user, user=request.user).exists()
    posts_list = user.posts.all()
    followers_count = Follow.objects.filter(author=user).count()
    following_count = Follow.objects.filter(user=user).count()
    paginator = Paginator(posts_list, 10)
    page_number = request.GET.get('page')
    page_count = paginator.per_page
    page = paginator.get_page(page_number)
    avatar = Avatar.objects.filter(profile=user)
    context = {'author': user, 'page': page, 'changes': 'profile',
               'avatar': avatar, 'count': page_count,
               'following': following,
               'followers_count': followers_count,
               'following_count': following_count}
    if user == request.user:
        if avatar.count() == 1:
            form = AvatarForm(request.POST or None,
                              files=request.FILES or None, instance=avatar[0])
            if form.is_valid():
                form.instance.profile = user
                form.save()
                return redirect('profile', username=user.username)
            added = {'form': form, }
            context.update(added)
            return render(request, 'profile.html', context)
        form = AvatarForm(request.POST or None, files=request.FILES or None)
        if form.is_valid():
            form.instance.profile = user
            form.save()
            return redirect('profile', username=user.username)
        added = {'form': form, }
        context.update(added)
        return render(request, 'profile.html', context)
    return render(request, 'profile.html', context)


def get_context(username, post_id):
    obj = get_object_or_404(Post, author__username=username, id=post_id)
    author = obj.author
    comments = obj.comments.all()
    form = PostForm(instance=obj)
    context = {'post': obj,
               'author': author,
               'form': form,
               'comments': comments,
               'changes': 'view', }
    return context


def post_view(request, username, post_id):
    context = get_context(username, post_id)
    edit = False
    user = get_object_or_404(User, username=username)
    post = get_object_or_404(Post, author__username=username, id=post_id)
    followers_count = Follow.objects.filter(author=post.author).count()
    following_count = Follow.objects.filter(user=post.author).count()
    avatar = Avatar.objects.filter(profile=user)
    form = CommentForm(request.POST or None)
    if user == request.user:
        edit = True
    if form.is_valid():
        form.instance.author = request.user
        form.instance.post = post
        form.save()
        return redirect('post', username=post.author.username,
                        post_id=post.id)
    added = {'form': form, 'followers_count': followers_count, 'edit': edit,
             'following_count': following_count, 'avatar': avatar, }
    context.update(added)
    return render(request, 'post.html', context)


@login_required
def add_comment(request, username, post_id):
    post = get_object_or_404(Post, author__username=username, id=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        form.instance.author = request.user
        form.instance.post = post
        form.save()
        return redirect('post', username=post.author.username,
                        post_id=post.id)
    return render(request, 'add_comment.html',
                  {'form': form, 'username': username, 'post': post, })


@login_required
def post_edit(request, username, post_id):
    context = get_context(username, post_id)
    post = context['post']
    if request.user != post.author:
        return redirect('index')
    form = PostForm(request.POST or None, files=request.FILES or None,
                    instance=post)
    if form.is_valid():
        form.save()
        return redirect('post', username=post.author.username,
                        post_id=post.id)
    return render(request, 'new.html', {'form': form, 'post': post,
                                        'changes': 'edit', })


def page_not_found(request, exception):
    return render(
        request,
        'misc/404.html',
        {'path': request.path},
        status=HTTPStatus.NOT_FOUND
    )


def server_error(request):
    return render(request, 'misc/500.html',
                  status=HTTPStatus.INTERNAL_SERVER_ERROR)


@login_required
def follow_index(request):
    posts = Post.objects.filter(author__following__user=request.user)
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, 'follow.html',
                  {'page': page,
                   'changes': 'index',
                   'paginator': paginator})


@login_required
def profile_follow(request, username):
    following_user = get_object_or_404(User, username=username)
    follower_user = request.user
    if following_user == follower_user or Follow.objects.filter(
            user=follower_user, author=following_user).exists():
        return redirect('profile', username=username)
    Follow.objects.create(user=follower_user, author=following_user)
    return redirect('profile', username=username)


@login_required
def profile_unfollow(request, username):
    following_user = get_object_or_404(User, username=username)
    follower_user = request.user
    follow = get_object_or_404(Follow, author=following_user,
                               user=follower_user)
    follow.delete()
    return redirect('profile', username=username)
