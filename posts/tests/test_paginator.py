from django.contrib.auth import get_user_model
from django.core.cache import cache
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
        batch_size = 13
        posts = [Post(text='Test %s' % i, group=cls.group,
                      author=cls.user) for i in range(batch_size)]
        Post.objects.bulk_create(posts, batch_size)

    def setUp(self):
        cache.clear()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_first_page_contains_ten_records(self):
        rev_names = (
            reverse('index'),
            reverse('group_posts', kwargs={'slug': self.group.slug, }),
            reverse('profile', kwargs={
                    'username': self.user.username, }),
        )

        for rev_name in rev_names:
            response = self.authorized_client.get(rev_name)
            first_count = response.context.get('count')
            second_count = Post.objects.count() - first_count
            indexes = {'?page=2': second_count,
                       '?page=1': first_count, }
            for index, count in indexes.items():
                with self.subTest():
                    response = self.authorized_client.get(
                        rev_name + index)

                    self.assertEqual(
                        len(response.context.get('page').object_list),
                        count)
