import time
from itertools import islice

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from posts.models import Group, Post

User = get_user_model()


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='Anon')
        cls.group = Group.objects.create(
            title='Название',
            slug='test-slug',
            description='Описание',
        )
        batch_size = 14
        posts = [Post(text='Test %s' % i, group=cls.group,
                      author=cls.user) for i in range(13)]
        batch = list(islice(posts, batch_size))
        Post.objects.bulk_create(batch, batch_size)

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_first_page_containse_ten_records(self):
        rev_names = (
            reverse('index'),
            reverse('group_posts', kwargs={'slug': self.group.slug, }),
            reverse('profile', kwargs={
                    'username': self.user.username, }),
        )
        time.sleep(21)
        for rev_name in rev_names:
            with self.subTest():
                response = self.authorized_client.get(rev_name)
                self.assertEqual(
                    len(response.context.get('page').object_list), 10)

    def test_second_page_containse_three_records(self):
        rev_names = (
            reverse('index'),
            reverse('group_posts', kwargs={'slug': self.group.slug, }),
            reverse('profile', kwargs={
                    'username': self.user.username, }),
        )
        for rev_name in rev_names:
            with self.subTest():
                response = self.authorized_client.get(rev_name + '?page=2')
                self.assertEqual(
                    len(response.context.get('page').object_list), 3)
