from django.test import TestCase
from django.urls import reverse

from posts.models import Post, User

AUTHOR_USERNAME = 'Andrey'
AUTHOR_PASSWORD = 'qwerty'

GROUP_SLUG = 'test-slug'


class RoutesTests(TestCase):
    def test_routes_point_to_desired_locaiton(self):
        """Маршрутизация выполняется корректно"""
        author = User.objects.create(
            username=AUTHOR_USERNAME,
            password=AUTHOR_PASSWORD
        )
        post = Post.objects.create(text='Текст', author=author)
        routes_urls = [
            [reverse('index'), '/'],
            [reverse('group', args=[GROUP_SLUG]),
             f'/group/{GROUP_SLUG}/'],
            [reverse('profile', args=[AUTHOR_USERNAME]),
             f'/{AUTHOR_USERNAME}/'],
            [reverse('post', args=[AUTHOR_USERNAME, post.id]),
             f'/{AUTHOR_USERNAME}/{post.id}/'],
            [reverse('new_post'), '/new/'],
            [reverse('post_edit', args=[AUTHOR_USERNAME, post.id]),
             f'/{AUTHOR_USERNAME}/{post.id}/edit/']
        ]
        for route, url in routes_urls:
            self.assertEqual(route, url)
