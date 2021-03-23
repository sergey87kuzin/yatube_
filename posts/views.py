from django.contrib.auth.decorators import login_required
from django.core.cache import cache
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from .forms import CommentForm, PostForm
from .models import Follow, Group, Post, User


def index(request):
    results = cache.get('index_page')
    if results is None:
        post_list = Post.objects.all()
        cache.set('index_page', post_list, 20)
    cached_list = cache.get('index_page')
    paginator = Paginator(cached_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request,
                  'index.html',
                  {'page': page,
                   'changes': 'index',
                   'paginator': paginator})


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts_list = group.posts.all()
    paginator = Paginator(posts_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, 'group.html', {'group': group,
                                          'page': page,
                                          'changes': 'index',
                                          'paginator': paginator})


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
    paginator = Paginator(posts_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, 'profile.html', {'author': user, 'page': page,
                                            'changes': 'profile',
                                            'following': following})


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
    post = get_object_or_404(Post, author__username=username, id=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        form.instance.author = request.user
        form.instance.post = post
        form.save()
        return redirect('add_comment', username=post.author.username,
                        post_id=post.id)
    context['form'] = form
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
                  {'form': form, })


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
        status=404
    )


def server_error(request):
    return render(request, 'misc/500.html', status=500)


@login_required
def follow_index(request):
    posts = []
    # authors = get_list_or_404(User, follower=request.user)
    follows = Follow.objects.filter(user=request.user)
    for follow in follows:
        author = follow.author
        author_posts = author.posts.all()
        posts.extend(author_posts)
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
    if following_user != follower_user:
        follow = Follow.objects.filter(
            user=follower_user, author=following_user)
        if follow:
            return redirect('index')
        Follow.objects.create(user=follower_user, author=following_user)
        return render(request, 'profile_follow.html', {'username': username})
    return redirect('index')


@login_required
def profile_unfollow(request, username):
    following_user = get_object_or_404(User, username=username)
    follower_user = request.user
    follow = get_object_or_404(Follow, author=following_user,
                               user=follower_user)
    follow.delete()
    return render(request, 'profile_unfollow.html', {'username': username})
