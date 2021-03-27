from django.test import TestCase
from posts.models import Comment, Group, Post, User


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title='Название',
            slug='Ссылка',
            description='Описание',
        )
        cls.user = User.objects.create(username='Anon')
        cls.post = Post.objects.create(
            text='Тестовый текст, который длиннее 15 символов',
            group=cls.group,
            author=cls.user,
        )

        cls.comment = Comment.objects.create(
            text='буду вторым',
            author=cls.user,
            post=cls.post
        )

    def test_post_verbose_name(self):
        """verbose_name в полях совпадает с ожидаемым."""
        post = PostModelTest.post
        field_verboses = {
            'text': 'Текст сообщения',
            'author': 'Автор поста',
            'group': 'Группа',
        }

        for value, expected in field_verboses.items():
            with self.subTest(value=value):

                self.assertEqual(
                    post._meta.get_field(value).verbose_name, expected)

    def test_group_verbose_name(self):
        """verbose_name в полях совпадает с ожидаемым."""
        group = PostModelTest.group
        field_verboses = {
            'title': 'имя группы',
            'description': 'описание группы',
        }

        for value, expected in field_verboses.items():
            with self.subTest(value=value):

                self.assertEqual(
                    group._meta.get_field(value).verbose_name, expected)

    def test_comment_verbose_name(self):
        """verbose_name в полях совпадает с ожидаемым."""
        comment = PostModelTest.comment
        text_verbose_name = 'Текст сообщения'

        self.assertEqual(comment._meta.get_field('text').verbose_name,
                         text_verbose_name)

    def test_name_field(self):
        group = PostModelTest.group
        post = PostModelTest.post
        names = {
            group.title: str(group),
            post.text[:15]: str(post),
        }

        for value, expected in names.items():
            with self.subTest(value=value):

                self.assertEqual(value, expected)

    def test_help_text(self):
        post = PostModelTest.post
        group = PostModelTest.group
        comment = PostModelTest.comment
        text_help_text = 'будьте вежливы. нас читают дети'
        help_texts = {
            post: 'text',
            group: 'description',
            comment: 'text',
        }

        for value, field in help_texts.items():
            with self.subTest(value=value):

                self.assertEqual(value._meta.get_field(field).help_text,
                                 text_help_text)
