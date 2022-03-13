from django.shortcuts import render, get_object_or_404, redirect
from .models import Post, Group, Comment, Follow
from .forms import PostForm, CommentForm
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.views.decorators.cache import cache_page

User = get_user_model()

@cache_page(20)
def index(request):
    post_list = Post.objects.all()
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get("page")
    page = paginator.get_page(page_number)
    return render(request, "index.html", {'page': page, 'paginator': paginator})

def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    post_list = group.posts.all()
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, "group.html", {'group': group, "page": page, "paginator": paginator})

@login_required
def new_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST, files=request.FILES or None)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('index')
    else:
        form = PostForm()
    return render(request, 'new.html', {'form': form, 'is_edit': False})

def profile(request, username):
    author = get_object_or_404(User, username=username)
    post_list = author.posts.all()
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    following = request.user.is_authenticated and Follow.objects.filter(user=request.user, author=author).exists()
    return render(request, 'profile.html', {'author': author, 'page': page, 'paginator': paginator,'following': following})

def post_view(request, username, post_id):
    post = get_object_or_404(Post.objects.select_related('author', 'group'), id=post_id, author__username=username)
    form = CommentForm()
    post_count = post.author.posts.all().count()
    return render(request, 'post.html', {"post": post, 'author': post.author, 'form': form, 'post_count': post_count})

@login_required
def post_edit(request, username, post_id):
    post = get_object_or_404(Post, id=post_id, author__username=username)
    if request.user != post.author:
        return redirect(reverse("post", kwargs={'username': username, 'post_id': post_id}))
    form = PostForm(request.POST or None, files=request.FILES or None, instance=post)
    if form.is_valid():
        form.save()
        return redirect(reverse ("post", kwargs={'username': username, 'post_id': post_id}))
    return render(request, "new.html", {'form': form, 'post': post, 'is_edit': True})

@login_required
def add_comment(request, username, post_id):
    post = get_object_or_404(Post, pk=post_id, author__username=username)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect(reverse ("post", kwargs={'username': username, 'post_id': post_id}))

@login_required
def follow_index(request):
    post_list = Post.objects.filter(author__following__user=request.user)
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, 'follow.html', {'page': page, 'paginator': paginator})

@login_required 
def profile_follow(request, username):
    user = request.user.id
    author = get_object_or_404(User, username=username)
    follow_check = Follow.objects.filter(user=user, author=author.id).count()
    if follow_check == 0 and request.user.username != username:
        following = Follow.objects.create(user=request.user, author=author)
        following.save()
    return redirect('profile', username=username)

@login_required
def profile_unfollow(request, username):
    follow = Follow.objects.filter(user=request.user.id, author=get_object_or_404(User, username=username))
    follow.delete()
    return redirect('profile', username=username)

def page_not_found(request, exception):
    return render(request, "misc/404.html", {"path": request.path}, status=404)

def server_error(request):
    return render(request, "misc/500.html", status=500)