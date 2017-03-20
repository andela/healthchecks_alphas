from django import forms

from .models import Comment

class BlogPostForm(forms.Form):
	title = forms.CharField(required=True)
	content = forms.CharField(required=True, widget=forms.Textarea)

class CommentForm(forms.ModelForm):

    class Meta:
        model = Comment
        fields = ('body',)