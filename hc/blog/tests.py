from django.test import TestCase

from .models import Post

class PostTestCase(TestCase):
    def test_string_representation(self):
        post = Post(title="Testing python apps using functional and unit testing")
        self.assertEqual(str(post), post.title)
