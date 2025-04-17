# blog/views.py
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import render, get_object_or_404, redirect
from .models import Post
from .forms import PostForm

# Student role permission decorator
def student_required(function):
    def wrap(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.role == 'student':
            return function(request, *args, **kwargs)
        else:
            raise PermissionDenied
    return wrap

# List all published posts
def post_list(request):
    posts = Post.objects.filter(published=True).order_by('-created_at')
    return render(request, 'blog/post_list.html', {'posts': posts})

# View a single post
def post_detail(request, pk):
    post = get_object_or_404(Post, pk=pk)
    return render(request, 'blog/post_detail.html', {'post': post})

# Create a new post (student only)
@login_required
@student_required
def post_create(request):
    if request.method == "POST":
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            # Correctly using the namespace
            return redirect('post_detail', pk=post.pk)
    else:
        form = PostForm()
    return render(request, 'blog/post_form.html', {'form': form})


@login_required
def post_delete(request, pk):
    post = get_object_or_404(Post, pk=pk)
    
    # Check if the user is the author
    if request.user != post.author:
        raise PermissionDenied
    
    # Handle deletion with confirmation
    if request.method == "POST":
        post.delete()
        return redirect('post_list')
    
    # GET request shows confirmation page
    return render(request, 'blog/post_confirm_delete.html', {'post': post})