from django.shortcuts import render, redirect, get_object_or_404, render_to_response
from django.views.generic import DetailView
from django.contrib.auth.decorators import login_required

from .models import Post
from .forms import BlogPostForm, CommentForm

# Create your views here.
def post_list(request):
    posts = Post.objects.order_by('-created_at')
    return render(request, "blog/blog.html", {"posts": posts})

class PostDetail(DetailView):
    model = Post

@login_required
def create_post(request):
	print("Create post!: ", request.POST)
	if request.method == 'POST':
		form = BlogPostForm(request.POST)
		if form.is_valid():
			title = form.cleaned_data['title']
			content = form.cleaned_data['content']
			print("title: ", title)
			print("content: ", content)
			new_post = Post(title=title, content=content, author=request.user)
			new_post.save()
			return redirect('/blog/{0}'.format(new_post.id))
	else:
		form = BlogPostForm()

	return render(request, 'blog/create.html', {'form': form})

def post_remove(request, pk):
	post = get_object_or_404(Post, pk=pk)
	post.delete()
	return redirect('/blog/', {'message':'Delete successful'})

def add_comment_to_post(request, pk):
	post = get_object_or_404(Post, pk=pk)
	if request.method == "POST":
		form = CommentForm(request.POST)
		if form.is_valid():
			comment = form.save(commit=False)
			comment.post = post
			comment.save()
			return redirect('post_detail', pk=post.pk)
	else:
		form = CommentForm()
	return render(request, 'blog/add_comment_to_post.html', {'form': form})
