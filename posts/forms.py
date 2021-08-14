from django.forms import ModelForm

from .models import Avatar, Comment, Post


class PostForm(ModelForm):
    class Meta:
        model = Post
        fields = ['group', 'text', 'image']


class CommentForm(ModelForm):
    class Meta:
        model = Comment
        fields = ['text']


class AvatarForm(ModelForm):
    class Meta:
        model = Avatar
        fields = ['image']
