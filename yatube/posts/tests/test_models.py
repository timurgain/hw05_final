from django.test import TestCase

from posts.models import Group, Post, User


GROUP_TITLE = 'Тест групп'
POST_TEXT = 'Ж' * 100
POST_STR = 'Ж' * 15
SLUG = 'test-slug'


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.test_user = User.objects.create(username='test', password='test')
        cls.test_post = Post.objects.create(author=cls.test_user,
                                            text=POST_TEXT)
        cls.test_group = Group.objects.create(title=GROUP_TITLE,
                                              description='Тестовое описание',
                                              slug=SLUG)

    def test_verbose_name_meta(self):
        """Checking the verbose_name _meta for the Post model fields."""
        post = PostModelTest.test_post
        field_verbose = {
            'text': 'Статья',
            'pub_date': 'Дата публикации',
            'author': 'Автор',
            'group': 'Группа',
        }
        for field, expected_value in field_verbose.items():
            with self.subTest(field=field):
                self.assertEqual(
                    post._meta.get_field(field).verbose_name, expected_value)

    def test_help_text_meta(self):
        """Checking the help_text _meta for the Post model fields."""
        post = PostModelTest.test_post
        field_help_text = {
            'text': 'Начни здесь свой шедевр',
            'group': 'Выбери группу',
        }
        for field, expected_value in field_help_text.items():
            with self.subTest(field=field):
                self.assertEqual(
                    post._meta.get_field(field).help_text, expected_value)

    def test_post_model_str_method(self):
        """Checking the __str__ method for the Post model."""
        posible_str = PostModelTest.test_post.text[:15]
        self.assertEqual(posible_str, POST_STR)

    def test_group_model_str_method(self):
        """Checking the __str__ method for the Group model."""
        posible_str = PostModelTest.test_group.title
        self.assertEqual(posible_str, GROUP_TITLE)
