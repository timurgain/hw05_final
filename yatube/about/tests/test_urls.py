from http import HTTPStatus
from django.test import TestCase, Client


class StaticURLTests(TestCase):
    def setUp(self):
        # имитация браузера
        self.guest_client = Client()

    def test_about_author(self):
        """Checking url /about/author/."""
        response = self.guest_client.get('/about/author/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_about_tech(self):
        """Checking url /about/tech/'."""
        response = self.guest_client.get('/about/tech/')
        self.assertEqual(response.status_code, HTTPStatus.OK)
