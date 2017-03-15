from django.test import TestCase
from django.contrib.auth import get_user_model

from .models import Post

class PostTestCase(TestCase):
    def test_string_representation(self):
        post = Post(title="Testing python apps using functional and unit testing")
        self.assertEqual(str(post), post.title)

    def test_verbose_name_plural(self):
        self.assertEqual(str(Post._meta.verbose_name_plural), "posts")

class BlogTestCases(TestCase):

    def setUp(self):
        self.user = get_user_model().objects.create(username="anonymous")
    '''
        Test that blog entries show up on post list page
    '''

    def test_basic_post_view(self):
        post = Post.objects.create(title="TIA", content="TIA content", author=self.user)
        response = self.client.get(post.get_absolute_url())
        self.assertEqual(response.status_code, 200)

    def test_get_absolute_url(self):
        post = Post.objects.create(title="My post title", author=self.user)
        self.assertIsNotNone(post.get_absolute_url())

    def test_title_in_post(self):
        post = Post.objects.create(title="TIA", content="TIA content", author=self.user)
        response = self.client.get(post.get_absolute_url())
        self.assertContains(response, post.title)

    def test_blog_page(self):
        response = self.client.get('/blog/')
        self.assertEqual(response.status_code, 200)

    def test_one_entry(self):
        Post.objects.create(title="TIA", content="TIA content", author=self.user)
        response = self.client.get("/blog/")
        self.assertContains(response, 'TIA')
        self.assertContains(response, 'TIA content')

    def test_no_entries(self):
        response = self.client.get('/blog/')
        self.assertContains(response, 'No blog posts yet')
