from __future__ import unicode_literals

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

    def __str__(self):
        '''
            Return a human readable representation of model instance
        '''
        return self.title
