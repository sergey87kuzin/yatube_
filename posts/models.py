from django.contrib.auth import get_user_model
from django.db import models

from .validators import validate_not_empty

User = get_user_model()


class Group(models.Model):
    title = models.CharField(verbose_name='имя группы', max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField(verbose_name='описание группы',
                                   help_text='будьте вежливы. нас читают дети')

    def __str__(self):
        return self.title


class Post(models.Model):
    text = models.TextField(validators=[validate_not_empty],
                            verbose_name='Текст сообщения',
                            help_text='будьте вежливы. нас читают дети')
    pub_date = models.DateTimeField('date published', auto_now_add=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               verbose_name='Автор поста',
                               related_name='posts')
    group = models.ForeignKey(Group, on_delete=models.SET_NULL,
                              verbose_name='Группа',
                              related_name='posts', blank=True, null=True,)
    image = models.ImageField(upload_to='posts/',
                              blank=True, null=True)

    class Meta:
        ordering = ('-pub_date',)

    def __str__(self):
        if len(self.text) >= 15:
            return self.text[:15]
        return self.text


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE,
                             related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name='comments')
    text = models.TextField(validators=[validate_not_empty],
                            verbose_name='Текст сообщения',
                            help_text='будьте вежливы. нас читают дети')
    created = models.DateTimeField('date published', auto_now_add=True)


class Follow(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,
                             related_name='follower')
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name='following')
