from django.core.cache import cache
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post, User

AUTHOR_USERNAME = 'Andrey'
AUTHOR_PASSWORD = 'qwerty'

GROUP_SLUG = 'test-slug'

INDEX_URL = reverse('index')


class CacheTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user_author = User.objects.create(
            username=AUTHOR_USERNAME,
            password=AUTHOR_PASSWORD
        )
        cls.group = Group.objects.create(
            title='Тестовое сообщество',
            slug=GROUP_SLUG
        )
        cls.post = Post.objects.create(
            text='Тестируем тестовую заметку',
            author=cls.user_author,
            group=cls.group
        )

    def setUp(self):
        self.guest_client = Client()
        self.author_client = Client()
        self.author_client.force_login(self.user_author)

    def test_new_post_creates_new_post(self):
        """Главная страница кэширует отображаемую информацию на 20 сек"""
        response_index_before_adding_post = self.guest_client.get(INDEX_URL)
        Post.objects.create(
            text='Тестовая заметка 2',
            author=self.user_author,
            group=self.group
        )
        response_index_after_adding_post = self.guest_client.get(INDEX_URL)
        self.assertEqual(
            response_index_before_adding_post.content,
            response_index_after_adding_post.content
        )
        cache.clear()
        response_index_after_cache_clear = self.guest_client.get(INDEX_URL)
        self.assertNotEqual(
            response_index_after_adding_post.content,
            response_index_after_cache_clear.content
        )
