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

    def test_post_help_text(self):
        """help_text в полях совпадает с ожидаемым."""
        post = PostModelTest.post
        text_help_text = "будьте вежливы. нас читают дети"
        self.assertEqual(post._meta.get_field('text').help_text,
                         text_help_text)

    def test_post_name_is_text_field(self):
        """В поле __str__  объекта post записано значение поля post.text."""
        post = PostModelTest.post
        short_post = post.text
        expected_object_name = short_post
        if len(post.text) >= 15:
            expected_object_name = post.text[:15]
        self.assertEqual(expected_object_name, str(post))

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

    def test_group_help_text(self):
        """help_text в полях совпадает с ожидаемым."""
        group = PostModelTest.group
        description_help_text = "будьте вежливы. нас читают дети"
        self.assertEqual(group._meta.get_field('description').help_text,
                         description_help_text)

    def test_group_name_is_title_field(self):
        """В поле __str__  объекта group записано значение поля group.title"""
        group = PostModelTest.group
        expected_object_name = group.title
        self.assertEqual(expected_object_name, str(group))

    def test_comment_help_text(self):
        """help_text в полях совпадает с ожидаемым."""
        comment = PostModelTest.comment
        text_help_text = "будьте вежливы. нас читают дети"
        self.assertEqual(comment._meta.get_field('text').help_text,
                         text_help_text)

    def test_group_verbose_name(self):
        """verbose_name в полях совпадает с ожидаемым."""
        comment = PostModelTest.comment
        text_verbose_name = 'Текст сообщения'
        self.assertEqual(comment._meta.get_field('text').verbose_name,
                         text_verbose_name)
