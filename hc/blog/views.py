from django.shortcuts import render, redirect
from django.views.generic import DetailView
from django.contrib.auth.decorators import login_required

from .models import Post
from .forms import BlogPostForm

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