from django.test import TestCase

from .models import Post

class PostTestCase(TestCase):
    def test_string_representation(self):
        post = Post(title="Testing python apps using functional and unit testing")
        self.assertEqual(str(post), post.title)

    def test_verbose_name_plural(self):
        self.assertEqual(str(Post._meta.verbose_name_plural), "posts")
