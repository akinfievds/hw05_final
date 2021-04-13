from django.test import Client, TestCase
from django.urls import reverse


class StaticViewsTest(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_about_pages_accessible_by_name(self):
        """URLs, генерируемые при помощи имен приложения about доступны"""
        names = [
            'about:author',
            'about:tech'
        ]
        for name in names:
            with self.subTest():
                response = self.guest_client.get(reverse(name))
                self.assertEqual(response.status_code, 200)

    def test_about_pages_templates_accessible_by_name(self):
        """Шаблоны страниц about доступны (по имени)"""
        names_templates = {
            'about:author': 'about/author.html',
            'about:tech': 'about/tech.html'
        }
        for name, template in names_templates.items():
            with self.subTest(name=name):
                response = self.guest_client.get(reverse(name))
                self.assertTemplateUsed(response, template)
