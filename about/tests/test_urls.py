from django.test import Client, TestCase


class StaticURLPages(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_about_pages_exists_at_desired_location(self):
        """Страницы приложения about доступны"""
        urls = [
            '/about/author/',
            '/about/tech/'
        ]
        for url in urls:
            with self.subTest():
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, 200)

    def test_about_pages_uses_correct_templates(self):
        """Шаблоны страниц about доступны (по адресу)"""
        urls_templates = {
            '/about/author/': 'about/author.html',
            '/about/tech/': 'about/tech.html'
        }
        for url, template in urls_templates.items():
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertTemplateUsed(response, template)
