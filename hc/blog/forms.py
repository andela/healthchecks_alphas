from django import forms

class BlogPostForm(forms.Form):
	title = forms.CharField(required=True)
	content = forms.CharField(required=True, widget=forms.Textarea)