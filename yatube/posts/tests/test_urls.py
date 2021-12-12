from http import HTTPStatus

from django.test import Client, TestCase

from posts.models import Group, Post, User


POST_GROUP_TITLE = 'Тест групп'
POST_TEXT = 'Ж' * 100
SLUG = 'test-slug'
AUTHOR = 'author'
POST_ID = '1'

URLS_TEMPLATE_EVERYONE = {
    f'/group/{SLUG}/': 'posts/group_list.html',
    f'/profile/{AUTHOR}/': 'posts/profile.html',
    f'/posts/{POST_ID}/': 'posts/post_detail.html',
    '/': 'posts/index.html',
}
URLS_TEMPLATE_AUTHORIZED = {
    '/create/': 'posts/create_post.html',
}
URLS_TEMPLATE_AUTHOR = {
    f'/posts/{POST_ID}/edit/': 'posts/create_post.html',
}
NON_EXISTING_URL = '/non_existing_url/'


class PostURLTest(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.auth_author = User.objects.create(username=AUTHOR)
        cls.auth_user = User.objects.create(username='auth_user')
        cls.post = Post.objects.create(author=cls.auth_author,
                                       text=POST_TEXT)
        cls.group = Group.objects.create(title=POST_GROUP_TITLE,
                                         description='Тестовое описание',
                                         slug=SLUG)
        # три браузера: гость, залогинен, автор-поста-залогинен
        cls.guest_client = Client()
        cls.auth_client = Client()
        cls.auth_client.force_login(cls.auth_user)
        cls.author_client = Client()
        cls.author_client.force_login(cls.auth_author)

    def test_posts_urls_for_guest(self):
        """Checking urls and templates for a guest user."""
        urls_templates = {
            **URLS_TEMPLATE_EVERYONE,
        }
        for url, template in urls_templates.items():
            with self.subTest(url=url):
                response = PostURLTest.guest_client.get(url)
                self.assertTemplateUsed(response, template)

    def test_posts_urls_for_auth(self):
        """Checking urls and templates for the authorized user."""
        urls_templates = {
            **URLS_TEMPLATE_EVERYONE,
            **URLS_TEMPLATE_AUTHORIZED,
        }
        for url, template in urls_templates.items():
            with self.subTest(url=url):
                response = PostURLTest.auth_client.get(url)
                self.assertTemplateUsed(response, template)

    def test_posts_urls_for_author(self):
        """Checking urls and templates for the author user."""
        urls_templates = {
            **URLS_TEMPLATE_EVERYONE,
            **URLS_TEMPLATE_AUTHORIZED,
            **URLS_TEMPLATE_AUTHOR,
        }
        for url, template in urls_templates.items():
            with self.subTest(url=url):
                response = PostURLTest.author_client.get(url)
                self.assertTemplateUsed(response, template)

    def test_posts_urls_redirect_for_guest(self):
        """Checking redirect urls for a guest user."""
        urls = {
            **URLS_TEMPLATE_AUTHORIZED,
            **URLS_TEMPLATE_AUTHOR,
        }
        for url in urls.keys():
            with self.subTest(url=url):
                response = PostURLTest.guest_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.FOUND)  # 302

    def test_posts_urls_redirect_for_auth(self):
        """Checking redirect urls for the authorized user."""
        urls = {
            **URLS_TEMPLATE_AUTHOR,
        }
        for url in urls.keys():
            with self.subTest(url=url):
                response = PostURLTest.auth_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.FOUND)  # 302

    def test_posts_urls_404(self):
        """Checking response 404 for non existing url."""
        response = PostURLTest.guest_client.get(NON_EXISTING_URL)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)  # 404
