from __future__ import unicode_literals
from django.core.urlresolvers import reverse

from django.db import models
from django.contrib.auth.models import User

class Post(models.Model):
    '''
        fields for Post field
    '''
    title = models.CharField(max_length=250)
    content = models.TextField()
    author = models.ForeignKey(User, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "posts"

    def __str__(self):
        '''
            Return a human readable representation of model instance
        '''
        return self.title

    def get_absolute_url(self):
        return reverse('post_detail', kwargs={'pk': self.pk})

class Comment(models.Model):
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    post = models.ForeignKey(Post, related_name='comments', null=True)

    def __str__(self):
        return self.body
