from django import forms
from django.db.models import Q

from .models import Post, Comment, Menu


class PostEditForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('name', 'description', 'content')


class MenuEditForm(forms.ModelForm):
    class Meta:
        model = Menu
        fields = ('name', 'parent', 'post')

    def __init__(self, *args, **kwargs):
        super(MenuEditForm, self).__init__(*args, **kwargs)
        self.fields['parent'].queryset = Menu.objects.exclude(
            Q(id__exact=self.instance.id) | Q(parent__isnull=False))


class CommentAddForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('content', 'parent')
