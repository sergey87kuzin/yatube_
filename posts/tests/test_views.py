import shutil
import tempfile
import time

from django import forms
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse
from posts.models import Follow, Group, Post, User


class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='Anon')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)
        cls.user_author = User.objects.create(username='Anon3')
        cls.author_client = Client()
        cls.author_client.force_login(cls.user_author)
        cls.user_not_follow = User.objects.create_user(username='Anon4')
        cls.auth_client = Client()
        cls.auth_client.force_login(cls.user)
        Follow.objects.create(
            author=cls.user,
            user=cls.user_author,
        )
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
            slug='test-slug',
            description='Описание',
        )
        cls.post = Post.objects.create(
            text='Тестовый текст, который длиннее 15 символов',
            group=cls.group,
            author=cls.user,
            image=cls.uploaded
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)

    def help_with_test(self, post_object):
        self.assertEqual(post_object.author, PostPagesTests.user)
        self.assertEqual(post_object.text, PostPagesTests.post.text)
        self.assertEqual(post_object.image, PostPagesTests.post.image)
        self.assertEqual(post_object.group, PostPagesTests.group)

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            'index.html': reverse('index'),
            'new.html': reverse('new_post'),
            'group.html': (
                reverse('group_posts', kwargs={'slug': self.group.slug})
            ),
            'follow.html': reverse('follow_index'),
            'profile_follow.html': reverse(
                'profile_follow',
                kwargs={'username': self.user_author.username}),
        }
        for template, reverse_name in templates_url_names.items():
            with self.subTest():
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_follow_uses_correct_template(self):
        response = self.author_client.get(
            reverse('profile_unfollow',
                    kwargs={'username': self.user.username}))
        self.assertTemplateUsed(response, 'profile_unfollow.html')

    def test_new_edit_page_show_correct_context(self):
        """Шаблон new, edit сформирован с правильным контекстом."""
        rev_names = (reverse('new_post'),
                     reverse('post_edit',
                     kwargs={'username': self.user.username,
                             'post_id': self.post.id}))
        for rev_name in rev_names:
            with self.subTest():
                response = self.authorized_client.get(rev_name)
                new_forms_fields = {
                    'text': forms.fields.CharField,
                    'group': forms.fields.ChoiceField,
                }
            for value, expected in new_forms_fields.items():
                with self.subTest(value=value):
                    model_field = response.context['form'].fields[value]
                    self.assertIsInstance(model_field, expected)

    def test_post_page_show_correct_context(self):
        """Шаблон post сформирован с правильным контекстом."""
        resp = self.authorized_client.get(reverse('post', kwargs={
                                                  'username':
                                                  self.user.username,
                                                  'post_id': self.post.id}))
        post_object = resp.context['post']
        PostPagesTests.help_with_test(self, post_object)

    def test_home_page_show_correct_context(self):
        resp = self.authorized_client.get(reverse('index'))
        post_object = resp.context['page'][0]
        PostPagesTests.help_with_test(self, post_object)

    def test_group_page_show_correct_context(self):
        resp = self.authorized_client.get(
            reverse('group_posts', kwargs={'slug': self.group.slug, }))
        post_object = resp.context['page'][0]
        PostPagesTests.help_with_test(self, post_object)
        group = resp.context['group']
        self.assertEqual(group, self.group)

    def test_profile_page_show_correct_context(self):
        resp = self.authorized_client.get(
            reverse('profile', kwargs={
                    'username': self.user.username, }))
        post_object = resp.context['page'][0]
        PostPagesTests.help_with_test(self, post_object)

    def test_to_follow(self):
        """авторизованные пользователи могут подписываться"""
        self.authorized_client.get(reverse(
            'profile_follow', kwargs={'username': self.user_author.username}))
        follow = Follow.objects.filter(
            user=self.user_author, author=self.user)
        self.assertTrue(follow.exists())

    def test_to_unfollow(self):
        """авторизованные пользователи могут отписываться"""
        self.author_client.get(reverse(
            'profile_unfollow',
            kwargs={'username': self.user.username}))
        follow = Follow.objects.filter(
            user=self.user_author, author=self.user)
        self.assertFalse(follow.exists())

    def test_follow_page_show_correct_context(self):
        """пост появился на странице подписанного пользователя"""
        resp = self.author_client.get(
            reverse('follow_index'))
        post_object = resp.context['page'][0]
        PostPagesTests.help_with_test(self, post_object)

    def test_non_follow_page_show_correct_context(self):
        """пост не появился на странице неподписанного пользователя"""
        resp = self.auth_client.get(
            reverse('follow_index'))
        self.assertEqual(len(resp.context.get('page').object_list), 0)

    def test_page_not_found_exists(self):
        response = self.authorized_client.get('/ы/')
        self.assertEqual(response.status_code, 404)

    def test_home_page_cacher(self):
        """список постов на главной странице кэшируется на 20 секунд"""
        response = self.authorized_client.get(reverse('index'))
        post_object = response.context['page'][0]
        self.assertNotEqual(post_object.text, PostPagesTests.post.text)
        time.sleep(21)
        response = self.authorized_client.get(reverse('index'))
        post_object = response.context['page'][0]
        PostPagesTests.help_with_test(self, post_object)
