import os
import shutil
import tempfile

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from posts.models import Group, Follow, Post, User
from posts.settings import PAGE_POSTS_COUNT

AUTHOR_USERNAME = 'Andrey'
AUTHOR_PASSWORD = 'qwerty'

OTHER_USERNAME = 'Petr'
OTHER_PASSWORD = 'qwerty'

GROUP_1_SLUG = 'test-slug'
GROUP_2_SLUG = 'test-slug-2'

POSTS_COUNT = PAGE_POSTS_COUNT * 2

INDEX_URL = reverse('index')
GROUP_1_URL = reverse('group', kwargs={'slug': GROUP_1_SLUG})
GROUP_2_URL = reverse('group', kwargs={'slug': GROUP_2_SLUG})
PROFILE_URL = reverse('profile', kwargs={'username': AUTHOR_USERNAME})
FOLLOW_INDEX = reverse('follow_index')

PROFILE_FOLLOW = reverse('profile_follow',
                         kwargs={'username': AUTHOR_USERNAME})
PROFILE_UNFOLLOW = reverse('profile_unfollow',
                           kwargs={'username': AUTHOR_USERNAME})

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)

IMAGE_FILE = (
    b'\x47\x49\x46\x38\x39\x61\x02\x00'
    b'\x01\x00\x80\x00\x00\x00\x00\x00'
    b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
    b'\x00\x00\x00\x2C\x00\x00\x00\x00'
    b'\x02\x00\x01\x00\x00\x02\x02\x0C'
    b'\x0A\x00\x3B'
)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class ViewsPagesTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create(
            username=AUTHOR_USERNAME,
            password=AUTHOR_PASSWORD
        )
        cls.follower = User.objects.create(
            username=OTHER_USERNAME,
            password=OTHER_PASSWORD
        )
        cls.group_1 = Group.objects.create(
            title='Тестовое сообщество',
            description='Тестируем описание группы',
            slug=GROUP_1_SLUG
        )
        cls.group_2 = Group.objects.create(
            title='Тестовое сообщество 2',
            description='Тестируем описание группы 2',
            slug=GROUP_2_SLUG
        )
        cls.image = SimpleUploadedFile(
            name='small.gif',
            content=IMAGE_FILE,
            content_type='image/gif'
        )
        cls.post = Post.objects.create(
            text='Тестируем тестовую заметку',
            author=cls.author,
            group=cls.group_1,
            image=cls.image
        )
        cls.POST_URL = reverse(
            'post',
            kwargs={'username': AUTHOR_USERNAME, 'post_id': cls.post.id}
        )

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def setUp(self):
        self.guest_client = Client()
        self.authorized_author = Client()
        self.authorized_author.force_login(self.author)
        self.authorized_follower = Client()
        self.authorized_follower.force_login(self.follower)

    def test_posts_available_on_desired_pages(self):
        """Страницы с лентами, содержат требуемые данные"""
        urls_context = [
            [INDEX_URL, 'page'],
            [GROUP_1_URL, 'page'],
            [PROFILE_URL, 'page'],
            [self.POST_URL, 'post'],
        ]
        for url, context_name in urls_context:
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                if context_name == 'page':
                    self.assertEqual(len(response.context['page']), 1)
                    post = response.context['page'].object_list[0]
                if context_name == 'post':
                    post = response.context['post']
                self.assertEqual(post.text, self.post.text)
                self.assertEqual(post.author, self.post.author)
                self.assertEqual(post.group, self.post.group)
                self.assertIn(
                    os.path.relpath(post.image.name, start='posts'),
                    os.listdir(os.path.join(settings.MEDIA_ROOT, 'posts'))
                )

    def test_group_pages_shows_group_information(self):
        """Информация о сообществах доступна на ожидаемых страницах"""
        response = self.guest_client.get(GROUP_1_URL)
        group = response.context['group']
        self.assertEqual(group.title, self.group_1.title)
        self.assertEqual(group.description, self.group_1.description)

    def test_posts_with_group_available_only_at_own_group_page(self):
        """Заметка доступа только на странице своего сообщества"""
        repsonse = self.guest_client.get(GROUP_2_URL)
        posts = repsonse.context['page']
        self.assertNotIn(self.post, posts)

    def test_author_available_on_desired_pages(self):
        """Информация об авторе доступна на ожидаемых страницах"""
        urls = [PROFILE_URL, self.POST_URL]
        for url in urls:
            with self.subTest(url=url):
                self.assertEqual(
                    self.guest_client.get(url).context['author'],
                    self.author
                )

    def test_post_available_on_follow_page(self):
        """Запись появляется только в ленте тех, кто подписан на автора"""
        self.authorized_follower.get(PROFILE_FOLLOW)
        author_index = self.authorized_author.get(FOLLOW_INDEX)
        follower_index = self.authorized_follower.get(FOLLOW_INDEX)
        self.assertIn(self.post, follower_index.context['page'])
        self.assertNotIn(self.post, author_index.context['page'])

    def test_authorized_user_can_follow_other(self):
        """Авторизованный пользователь может подписаться на других"""
        follow_count_before = Follow.objects.filter(author=self.author).count()
        self.authorized_follower.get(PROFILE_FOLLOW)
        self.assertTrue(
            Follow.objects.filter(
                user=self.follower,
                author=self.author
            ).exists()
        )
        follow_count_after = Follow.objects.filter(author=self.author).count()
        self.assertNotEqual(follow_count_before, follow_count_after)
        self.assertEqual(follow_count_after, follow_count_before + 1)

    def test_authorized_user_can_unfollow_another(self):
        """Авторизованный пользователь может отписать от других"""
        self.authorized_follower.get(PROFILE_FOLLOW)
        self.assertTrue(
            Follow.objects.filter(
                user=self.follower,
                author=self.author
            ).exists()
        )
        follow_count_before = Follow.objects.filter(author=self.author).count()
        self.authorized_follower.get(PROFILE_UNFOLLOW)
        self.assertFalse(
            Follow.objects.filter(
                user=self.follower,
                author=self.author
            ).exists()
        )
        follow_count_after = Follow.objects.filter(author=self.author).count()
        self.assertNotEqual(follow_count_before, follow_count_after)
        self.assertEqual(follow_count_after, follow_count_before - 1)


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(
            username=AUTHOR_USERNAME,
            password=AUTHOR_PASSWORD
        )
        for i in range(1, POSTS_COUNT):
            cls.posts = Post.objects.create(text=f'Пост {i}', author=cls.user)

    def setUp(self):
        self.guest_client = Client()

    def test_first_page_contains_desired_amount_posts(self):
        """На главной странице отображается ожидаемое кол-во записей"""
        response = self.guest_client.get(INDEX_URL)
        self.assertLessEqual(
            response.context['page'].end_index(),
            PAGE_POSTS_COUNT
        )
