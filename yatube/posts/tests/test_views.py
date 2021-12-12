import shutil
import tempfile

from http import HTTPStatus

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.cache import cache
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from posts.forms import PostForm, CommentForm
from posts.models import Group, Post, User, Follow


POST_GROUP_TITLE = 'Тест групп'
POST_TEXT = 'Пост для тестов'
SLUG = 'test-slug'
AUTHOR = 'author'
AUTH_USER = 'auth_user'
IMAGE_GIF = (b'\x47\x49\x46\x38\x39\x61\x02\x00'
             b'\x01\x00\x80\x00\x00\x00\x00\x00'
             b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
             b'\x00\x00\x00\x2C\x00\x00\x00\x00'
             b'\x02\x00\x01\x00\x00\x02\x02\x0C'
             b'\x0A\x00\x3B')
IMAGE_NAME = 'small.gif'

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostViewsTest(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.auth_author = User.objects.create(username=AUTHOR)
        cls.auth_user = User.objects.create(username=AUTH_USER)
        cls.group = Group.objects.create(
            title=POST_GROUP_TITLE,
            description='Тестовое описание',
            slug=SLUG,
        )
        cls.group_wrong = Group.objects.create(
            title=f'{POST_GROUP_TITLE}, wrong',
            description='Тестовое описание',
            slug=f'{SLUG}-wrong',
        )
        cls.uploaded_img = SimpleUploadedFile(
            name=IMAGE_NAME,
            content=IMAGE_GIF,
            content_type='image/gif')
        # Посты c группой, author, с меткой от 1 до 13
        cls.author_posts = []
        for i in range(1, 14):
            cls.post = Post.objects.create(author=cls.auth_author,
                                           text=f'{POST_TEXT}, {i}',
                                           group_id=cls.group.id,
                                           image=cls.uploaded_img,)
            cls.author_posts.append(cls.post)
        # Посты с wrong-группой, user, с меткой от 14 до 26
        cls.posts_auth_user = []
        for i in range(14, 27):
            cls.post = Post.objects.create(author=cls.auth_user,
                                           text=f'{POST_TEXT}, {i}',
                                           group_id=cls.group_wrong.id,
                                           image=cls.uploaded_img,)
            cls.posts_auth_user.append(cls.post)
        cls.first_post_id = Post.objects.earliest('pub_date').id

        cls.author_client = Client()
        cls.author_client.force_login(cls.auth_author)

    @classmethod
    def tearDownClass(cls) -> None:
        super().tearDownClass()
        # удаляем папку для тестов
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def test_posts_views_templates(self):
        """Checking views, url names and templates for author user."""
        url_names_templates = {
            reverse('posts:index'
                    ): 'posts/index.html',
            reverse('posts:group_list',
                    kwargs={'sl': SLUG}
                    ): 'posts/group_list.html',
            reverse('posts:profile',
                    kwargs={'username': AUTHOR}
                    ): 'posts/profile.html',
            reverse('posts:post_detail',
                    kwargs={'id': PostViewsTest.first_post_id}
                    ): 'posts/post_detail.html',
            reverse('posts:post_create'
                    ): 'posts/create_post.html',
            reverse('posts:post_edit',
                    kwargs={'id': PostViewsTest.first_post_id}
                    ): 'posts/create_post.html',
        }
        for url_name, template in url_names_templates.items():
            with self.subTest(url_name=url_name):
                response = PostViewsTest.author_client.get(url_name)
                self.assertTemplateUsed(response, template)

    def test_index_context(self):
        """Checking context for main page."""
        response = PostViewsTest.author_client.get(reverse('posts:index'))
        first_object = response.context['page_obj'][0]
        self.assertEqual(first_object.text,
                         Post.objects.latest('pub_date').text)
        self.assertEqual(first_object.author.username, AUTH_USER)
        self.assertTrue(first_object.image)

    def test_index_paginator(self):
        """Checking paginator for main page."""
        response_page_1 = PostViewsTest.author_client.get(
            reverse('posts:index'))
        response_page_3 = PostViewsTest.author_client.get(
            reverse('posts:index') + '?page=3')
        self.assertEqual(len(response_page_1.context['page_obj']), 10)
        self.assertEqual(len(response_page_3.context['page_obj']), 6)

    def test_group_list_context(self):
        """Checking context for group_list page."""
        response = PostViewsTest.author_client.get(
            reverse('posts:group_list', kwargs={'sl': SLUG}))
        first_object = response.context['page_obj'][0]
        self.assertEqual(first_object.group.title, POST_GROUP_TITLE)
        self.assertEqual(first_object.author.username, AUTHOR)
        self.assertTrue(first_object.image)

    def test_group_list_paginator(self):
        """Checking paginator for group_list page."""
        response_page_1 = PostViewsTest.author_client.get(
            reverse('posts:group_list', kwargs={'sl': SLUG}))
        response_page_2 = PostViewsTest.author_client.get(
            reverse('posts:group_list', kwargs={'sl': SLUG}) + '?page=2')
        self.assertEqual(len(response_page_1.context['page_obj']), 10)
        self.assertEqual(len(response_page_2.context['page_obj']), 3)

    def test_profile_context(self):
        """Checking context for profile page."""
        response = PostViewsTest.author_client.get(
            reverse('posts:profile', kwargs={'username': AUTHOR}))
        first_object = response.context['page_obj'][0]
        self.assertEqual(first_object.author.username, AUTHOR)
        self.assertEqual(first_object.text,
                         PostViewsTest.author_posts[12].text)
        self.assertTrue(first_object.image)

    def test_profile_paginator(self):
        """Checking paginator for profile page."""
        response_page_1 = PostViewsTest.author_client.get(
            reverse('posts:profile', kwargs={'username': AUTHOR}))
        response_page_2 = PostViewsTest.author_client.get(
            reverse('posts:profile', kwargs={'username': AUTHOR}) + '?page=2')
        self.assertEqual(len(response_page_1.context['page_obj']), 10)
        self.assertEqual(len(response_page_2.context['page_obj']), 3)

    def test_post_detail_context(self):
        """Checking context (post, comment_form) for post_detail page."""
        response = PostViewsTest.author_client.get(
            reverse('posts:post_detail',
                    kwargs={'id': PostViewsTest.first_post_id}))
        response_text = response.context.get('post').text
        original_text = PostViewsTest.author_posts[0].text
        self.assertEqual(
            response_text, original_text)
        self.assertTrue(
            response.context.get('post').image)
        self.assertIsInstance(
            response.context.get('comment_form'), CommentForm)

    def test_post_create_view_form_class(self):
        """Checking post_create form class type in context."""
        response = PostViewsTest.author_client.get(
            reverse('posts:post_create'))
        self.assertIsInstance(
            response.context.get('form'), PostForm)

    def test_post_create_view_context(self):
        """Checking post_create view."""
        before_create = Post.objects.count()
        form_data = {
            'text': f'{POST_TEXT}, views.post_create',
            'group': PostViewsTest.group.id
        }
        response = PostViewsTest.author_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertEqual(
            response.status_code, HTTPStatus.OK)
        self.assertRedirects(
            response, reverse('posts:profile', kwargs={'username': AUTHOR}))
        self.assertEqual(
            Post.objects.count(), before_create + 1)
        self.assertEqual(
            form_data['text'], response.context['page_obj'][0].text)
        # Задание 3.
        latest_post = Post.objects.latest('pub_date')
        response_main_page = PostViewsTest.author_client.get(
            reverse('posts:index'))
        self.assertTrue(
            latest_post in response_main_page.context['page_obj'])
        response_group_page = PostViewsTest.author_client.get(
            reverse('posts:group_list', kwargs={'sl': SLUG}))
        self.assertTrue(
            latest_post in response_group_page.context['page_obj'])
        response_author_page = PostViewsTest.author_client.get(
            reverse('posts:profile', kwargs={'username': AUTHOR}))
        self.assertTrue(
            latest_post in response_author_page.context['page_obj'])
        response_wrong_group = PostViewsTest.author_client.get(
            reverse('posts:group_list', kwargs={'sl': f'{SLUG}-wrong'}))
        self.assertTrue(
            latest_post not in response_wrong_group.context['page_obj'])

    def test_post_edit_view_form_class(self):
        """Checking post_edit form class type in context."""
        response = PostViewsTest.author_client.get(
            reverse('posts:post_edit',
                    kwargs={'id': PostViewsTest.first_post_id}
                    )
        )
        self.assertIsInstance(
            response.context.get('form'), PostForm)

    def test_post_edit_context(self):
        """Checking post_edit context."""
        form_update = {
            'text': f'{POST_TEXT}, views.post_edit',
        }
        response = PostViewsTest.author_client.post(
            reverse('posts:post_edit',
                    kwargs={'id': PostViewsTest.first_post_id}),
            data=form_update,
            follow=True,
        )
        self.assertEqual(
            response.status_code, HTTPStatus.OK)
        self.assertRedirects(
            response,
            reverse(
                'posts:post_detail',
                kwargs={'id': PostViewsTest.first_post_id}
            )
        )
        self.assertEqual(response.context['post'].text, form_update['text'])


class TestCache(TestCase):
    def setUp(self) -> None:
        self.auth_author = User.objects.create(username=AUTHOR)
        self.guest_client = Client()
        cache.clear()

    def test_cache_on_main_page(self):
        """Checking cache in template on main page, while the cache is alive,
        then after cache is clear."""
        post_text = f'{POST_TEXT} кэш'

        # создали пост, обратильсь к странице - кэш создался
        post = Post.objects.create(
            author=self.auth_author, text=post_text)
        response_before = self.guest_client.get(reverse('posts:index'))
        self.assertContains(response_before, post_text)

        # удаляем пост из БД - но кэш должен все еще вернуть удаленный пост
        post.delete()
        response_after = self.guest_client.get(reverse('posts:index'))
        self.assertContains(response_after, post_text)

        # очистка кэша - удаленный еще раньше пост теперь и в кэше отсутствует
        cache.clear()
        response_cache_clear = self.guest_client.get(reverse('posts:index'))
        self.assertNotContains(response_cache_clear, post_text)


class TestFollow(TestCase):
    def setUp(self) -> None:
        # пользователи
        self.auth_author = User.objects.create(
            username=AUTHOR)
        self.auth_wrong_author = User.objects.create(
            username=f'wrong {AUTHOR}')
        self.auth_user = User.objects.create(
            username=AUTH_USER)
        # посты
        self.author_post = Post.objects.create(
            author=self.auth_author, text=f'{POST_TEXT}')
        self.wrong_author_post = Post.objects.create(
            author=self.auth_wrong_author, text=f'wrong {POST_TEXT}')
        # браузер
        self.user_client = Client()
        self.user_client.force_login(self.auth_user)

        cache.clear()

    def test_follow_creates_db_record(self):
        """auth_user starts following auth_author, db created."""
        before = Follow.objects.count()
        self.user_client.get(
            reverse(
                'posts:profile_follow',
                kwargs={'username': self.auth_author.username}
            )
        )
        after = Follow.objects.count()
        self.assertEqual(after, before + 1)

    def test_unfollow_deletes_db_record(self):
        """auth_user cancels following auth_author, db deleted."""
        before_creation = Follow.objects.count()
        # follow
        self.user_client.get(
            reverse(
                'posts:profile_follow',
                kwargs={'username': self.auth_author.username}
            )
        )
        # unfollow
        self.user_client.get(
            reverse(
                'posts:profile_unfollow',
                kwargs={'username': self.auth_author.username}
            )
        )
        after_deletion = Follow.objects.count()
        self.assertEqual(before_creation, after_deletion)

    def test_follow_index(self):
        """follow_index page shows the posts of only followed authors."""
        # подписка
        self.user_client.get(
            reverse(
                'posts:profile_follow',
                kwargs={'username': self.auth_author.username}
            )
        )
        response = self.user_client.get(
            reverse('posts:follow_index')
        )
        self.assertIn(self.author_post, response.context['page_obj'])
        self.assertNotIn(self.wrong_author_post, response.context['page_obj'])

    def test_main_index(self):
        """main index page shows the posts of all authors."""
        # подписка
        self.user_client.get(
            reverse(
                'posts:profile_follow',
                kwargs={'username': self.auth_author.username}
            )
        )
        response = self.user_client.get(
            reverse('posts:index')
        )
        self.assertIn(self.author_post, response.context['page_obj'])
        self.assertIn(self.wrong_author_post, response.context['page_obj'])
