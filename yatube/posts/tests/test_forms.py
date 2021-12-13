import shutil
import tempfile

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile

from django.test import TestCase, Client, override_settings
from django.urls.base import reverse

from posts.models import Post, User, Group, Comment


POST_GROUP_TITLE = 'Тест групп'
POST_TEXT = 'Пост для тестов'
SLUG = 'test-slug'
AUTHOR = 'author'
COMMENT = 'твой коммент'
FORM_VALID_ERROR_MSG = 'Обязательное поле.'
IMAGE_GIF = (b'\x47\x49\x46\x38\x39\x61\x02\x00'
             b'\x01\x00\x80\x00\x00\x00\x00\x00'
             b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
             b'\x00\x00\x00\x2C\x00\x00\x00\x00'
             b'\x02\x00\x01\x00\x00\x02\x02\x0C'
             b'\x0A\x00\x3B')
IMAGE_NAME = 'small.gif'

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class TestPostForm(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.auth_author = User.objects.create(username=AUTHOR)
        cls.group = Group.objects.create(
            title=POST_GROUP_TITLE,
            description='Тестовое описание',
            slug=SLUG,
        )
        cls.post = Post.objects.create(
            text=POST_TEXT,
            author=cls.auth_author,
            group_id=cls.group.id,
        )
        cls.author_client = Client()
        cls.author_client.force_login(cls.auth_author)

    @classmethod
    def tearDownClass(cls) -> None:
        super().tearDownClass()
        # удаляем папку для тестов
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def test_valid_form_post_create(self):
        """Checking the valid form on the post_create page,
        adds one db record."""
        db_before = Post.objects.count()
        text_jast_created = f'{POST_TEXT} создан'
        uploaded_img = SimpleUploadedFile(
            name=IMAGE_NAME,
            content=IMAGE_GIF,
            content_type='image/gif')
        form_record = {
            'text': text_jast_created,
            'group': TestPostForm.group.id,
            'image': uploaded_img,
        }
        TestPostForm.author_client.post(
            reverse('posts:post_create'), data=form_record, follow=True
        )
        db_after = Post.objects.count()
        self.assertEqual(
            db_after, db_before + 1)
        self.assertEqual(
            Post.objects.latest('pk').text, text_jast_created)
        self.assertTrue(
            Post.objects.filter(text=text_jast_created).exists())
        self.assertTrue(
            Post.objects.filter(image=f'posts/{uploaded_img.name}').exists())

    def test_not_valid_form_post_create(self):
        """Checking Not valid form with empty text-field
        on the post_create page, without db record."""
        db_before = Post.objects.count()
        form_create_record = {
            'text': '', 'group': TestPostForm.group.id,
        }
        response = TestPostForm.author_client.post(
            reverse('posts:post_create'), data=form_create_record, follow=True
        )
        db_after = Post.objects.count()
        self.assertEqual(
            db_after, db_before)
        self.assertFormError(
            response, 'form', 'text', FORM_VALID_ERROR_MSG)

    def test_valid_form_post_edit(self):
        """Checking the valid form on the post_edit page, updates db record."""
        db_before = Post.objects.count()
        text_jast_updated = f'{POST_TEXT}, обновлен'
        uploaded_img = SimpleUploadedFile(
            name=f'edit_{IMAGE_NAME}',
            content=IMAGE_GIF,
            content_type='image/gif')
        form_update = {
            'text': text_jast_updated,
            'group': TestPostForm.group.id,
            'image': uploaded_img,
        }
        TestPostForm.author_client.post(
            reverse(
                'posts:post_edit', kwargs={'id': TestPostForm.post.id}
            ), data=form_update, follow=True
        )
        db_after = Post.objects.count()
        self.assertEqual(
            db_after, db_before)
        self.assertTrue(
            Post.objects.filter(text=text_jast_updated).exists())
        self.assertTrue(
            Post.objects.filter(image=f'posts/{uploaded_img.name}').exists())

    def test_not_valid_form_post_edit(self):
        """Checking not valid form on the post_edit page,
        doesnt update db record."""
        db_before = Post.objects.count()
        form_update = {
            'text': '', 'group': TestPostForm.group.id,
        }
        response = TestPostForm.author_client.post(
            reverse(
                'posts:post_edit', kwargs={'id': TestPostForm.post.id}
            ), data=form_update, follow=True
        )
        db_after = Post.objects.count()
        self.assertEqual(
            db_after, db_before)
        self.assertFormError(
            response, 'form', 'text', FORM_VALID_ERROR_MSG)


class TestComment(TestCase):
    def setUp(self) -> None:
        self.auth_author = User.objects.create(username=AUTHOR)
        self.post = Post.objects.create(
            author=self.auth_author, text=f'{POST_TEXT}')
        self.guest_client = Client()
        self.author_client = Client()
        self.author_client.force_login(self.auth_author)

    def test_comments_form_auth_user(self):
        """
        Checking with auth_user comment posting via comment_form
        on post_detail/add_comment url, create db record.
        Then checking this comment on post_detail page.
        """
        comments_before = Comment.objects.count()
        jast_created_comment = f'{COMMENT} автора'
        comment_form_create = {
            'text': jast_created_comment
        }
        # записать коммент через форму на сайте
        self.author_client.post(
            reverse('posts:add_comment', kwargs={'post_id': self.post.id}),
            data=comment_form_create,
            follow=True
        )
        comments_after = Comment.objects.count()
        self.assertEqual(
            comments_after, comments_before + 1)
        self.assertTrue(
            Comment.objects.filter(text=jast_created_comment).exists())

        # и проверить коммент на странице post_detail
        response_post_detail = self.author_client.get(
            reverse('posts:post_detail', kwargs={'id': self.post.id}),)
        self.assertContains(response_post_detail, jast_created_comment)

    def test_comments_form_guest_user(self):
        """Checking comment_form with guest_user on post_detail/add_comment url,
        doesnt create db record.
        """
        comments_before = Comment.objects.count()
        comment_form_create = {
            'text': f'{COMMENT}'
        }
        self.guest_client.post(
            reverse('posts:add_comment', kwargs={'post_id': self.post.id}),
            data=comment_form_create,
            follow=True
        )
        comments_after = Comment.objects.count()
        self.assertEqual(comments_after, comments_before)
