from django.test import TestCase
from django.test.client import Client
from django.urls import reverse


class TestStaticViews(TestCase):
    def setUp(self):
        self.client = Client()

    def test_about_author(self):
        """Checking the view about:author."""
        response = self.client.get(reverse('about:author'))
        self.assertTemplateUsed(response, 'about/author.html')

    def test_about_tech(self):
        """Checking the view about:tech."""
        response = self.client.get(reverse('about:tech'))
        self.assertTemplateUsed(response, 'about/tech.html')
