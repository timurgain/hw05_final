from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls.base import reverse, reverse_lazy

from .forms import CreationForm

User = get_user_model()


class TestUserForm(TestCase):
    def setUp(self):
        self.client = Client()
        self.form = CreationForm()

    def test_user_signup_form(self):
        """Checking creation a new user via signup form."""
        db_before = User.objects.count()
        form = {
            'username': 'test_name',
            'password1': 'test_password12',
            'password2': 'test_password12',
        }
        response = self.client.post(
            reverse('users:signup'),
            data=form,
            follow=True,
        )
        db_after = User.objects.count()
        smth = 'smth'
        self.assertEqual(db_after, db_before + 1)
        self.assertRedirects(response, reverse_lazy('posts:index'))
        self.assertIn('mt', smth)
