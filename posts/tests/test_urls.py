from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from posts.models import Follow, Group, Post

User = get_user_model()


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user_author = User.objects.create(username='Anon2')
        cls.author_client = Client()
        cls.author_client.force_login(cls.user_author)
        cls.user = User.objects.create_user(username='NeAnon')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)
        Follow.objects.create(
            author=cls.user_author,
            user=cls.user,
        )
        Follow.objects.create(
            user=cls.user_author,
            author=cls.user,
        )
        cls.group = Group.objects.create(
            title='Название',
            slug='test-slug',
            description='Описание',
        )
        cls.post = Post.objects.create(
            text='Тестовый текст, который длиннее 15 символов',
            group=cls.group,
            author=cls.user_author,
        )

    def setUp(self):
        self.guest_client = Client()

    def test_url_exists_at_desired_location(self):
        """Доступ к страницам неавторизованного пользователя"""
        url_names = {
            '/': 200,
            f'/group/{ self.group.slug }/': 200,
            f'/{ self.user_author.username }/': 200,
            f'/{ self.user_author.username }/{ self.post.id }/': 200,
            '/new/': 302,
            f'/{ self.user_author.username }/{ self.post.id }/edit/': 302,
            '/follow/': 302,
            f'/{ self.user_author.username }/follow/': 302,
            f'/{ self.user_author.username }/unfollow/': 302,
            f'/{ self.user_author.username }/{ self.post.id }/comment/': 302
        }
        for url_name, page_code in url_names.items():
            with self.subTest():
                response = self.guest_client.get(url_name)
                self.assertEqual(response.status_code, page_code)

    def test_new_url_exists_at_desired_location(self):
        """Страницы доступны авторизованному пользователю."""
        url_names = {
            '/new/': 200,
            '/follow/': 200,
            f'/{ self.user_author.username }/follow/': 200,
            f'/{ self.user_author.username }/{ self.post.id }/comment/': 200
        }
        for url_name, page_code in url_names.items():
            with self.subTest():
                response = self.authorized_client.get(url_name)
                self.assertEqual(response.status_code, page_code)

    def test_edit_url_not_available(self):
        """Страница не доступна авторизованному неавтору поста"""
        resp = self.authorized_client.get(
            reverse('post_edit', kwargs={'username': self.user_author.username,
                                         'post_id': self.post.id}))
        self.assertEqual(resp.status_code, 302)

    def test_edit_url_available(self):
        """Страница доступна авторизованному автору поста"""
        response = self.author_client.get(
            reverse('post_edit', kwargs={'username': self.user_author.username,
                                         'post_id': self.post.id}))
        self.assertEqual(response.status_code, 200)

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            '/': 'index.html',
            f'/group/{ self.group.slug }/': 'group.html',
            '/new/': 'new.html',
            f'/{ self.user_author.username }/{ self.post.id }/edit/':
            'new.html',
            '/follow/': 'follow.html',
            f'/{ self.user_author.username }/follow/': 'profile_follow.html',
            f'/{ self.user_author.username }/unfollow/':
            'profile_unfollow.html',
            f'/{ self.user_author.username }/{ self.post.id }/comment/':
            'add_comment.html'
        }
        for reverse_name, template in templates_url_names.items():
            with self.subTest():
                response = self.author_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_edit_redirect(self):
        resp = self.authorized_client.get(
            reverse('post_edit', kwargs={'username': self.user_author.username,
                                         'post_id': self.post.id}))
        self.assertRedirects(resp, reverse('index'))
