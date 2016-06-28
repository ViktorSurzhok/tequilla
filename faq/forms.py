from django import forms

from .models import Post, Comment


class PostEditForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('name', 'description', 'content')


class CommentAddForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('content', 'parent')
