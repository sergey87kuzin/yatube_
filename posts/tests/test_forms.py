import shutil
import tempfile

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse
from posts.models import Comment, Group, Post, User


class PostFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='Anon')
        settings.MEDIA_ROOT = tempfile.mkdtemp(dir='media')
        cls.small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=cls.small_gif,
            content_type='image/gif'
        )
        cls.group = Group.objects.create(
            title='Название',
            slug='Ссылка',
            description='Описание',
        )
        cls.post = Post.objects.create(
            text='Тестовый текст, который длиннее 15 символов',
            group=cls.group,
            author=cls.user,
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)

    def test_create_post(self):
        """Валидная форма создает запись в posts."""
        posts_count = Post.objects.count()
        form_data = {
            'group': self.group.id,
            'text': 'Тестовый текст, который длиннее 15 символов',
            'image': PostFormTests.uploaded,
        }
        response = self.authorized_client.post(
            reverse('new_post'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse('index'))
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(
            Post.objects.filter(
                author=self.user,
                text=self.post.text,
                group=self.group.id,
                image='posts/small.gif',
            ).exists()
        )

    def test_edit_post(self):
        """Валидная форма редактирует запись в posts."""
        posts_count = Post.objects.count()
        group_post_count = Post.objects.filter(
            author=self.user,
            text=self.post.text,
        ).count()
        form_data = {
            'group': self.group.id,
            'text': 'Тестовый текст, который намного длиннее 15 символов',
        }
        response = self.authorized_client.post(
            reverse('post_edit', kwargs={'username': self.user.username,
                                         'post_id': self.post.id}),
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response, reverse('post', kwargs={'username': self.user.username,
                                              'post_id': self.post.id}))
        self.assertEqual(Post.objects.count(), posts_count)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(
            Post.objects.filter(
                author=self.user,
                text=form_data['text'],
                group=self.group.id,
            ).exists()
        )
        self.assertTrue(
            Post.objects.filter(
                author=self.user,
                text=form_data['text'],
            ).count() == group_post_count
        )

    def test_create_comment(self):
        """Валидная форма создает запись в comments."""
        comments_count = Comment.objects.count()
        form_data = {
            'text': 'первый, ах!',
            'post': PostFormTests.post,
        }
        response = self.authorized_client.post(
            reverse('add_comment',
                    kwargs={'username': self.user.username,
                            'post_id': self.post.id}),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse(
            'post', kwargs={'username': self.user.username,
                            'post_id': self.post.id}))
        self.assertEqual(Comment.objects.count(), comments_count + 1)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(
            Comment.objects.filter(
                author=self.user,
                text=form_data['text'],
                post=self.post,
            ).exists()
        )
