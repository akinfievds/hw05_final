from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post, User

AUTHOR_USERNAME = 'Andrey'
AUTHOR_PASSWORD = 'qwerty'

USER_USERNAME = 'Petr'
USER_PASSWORD = 'qwerty123'

GROUP_SLUG = 'test-slug'

LOGIN_URL = reverse('login')
INDEX_URL = reverse('index')
GROUP_URL = reverse('group', kwargs={'slug': GROUP_SLUG})
PROFILE_URL = reverse('profile', kwargs={'username': USER_USERNAME})
NEW_POST_URL = reverse('new_post')
NEW_POST_REDIRECT = f'{LOGIN_URL}?next={NEW_POST_URL}'

WRONG_URL = '/wrong-author/wrong-post-id/'

FOLLOW_INDEX = reverse('follow_index')
PROFILE_FOLLOW_URL = reverse(
    'profile_follow',
    kwargs={'username': AUTHOR_USERNAME}
)
PROFILE_FOLLOW_NONE_AUTHENTICATE_REDIRECT = '{}?next={}'.format(
    LOGIN_URL,
    PROFILE_FOLLOW_URL
)
PROFILE_UNFOLLOW_URL = reverse(
    'profile_unfollow',
    kwargs={'username': AUTHOR_USERNAME}
)
PROFILE_UNFOLLOW_NONE_AUTENTICATE_REDIRECT = '{}?next={}'.format(
    LOGIN_URL,
    PROFILE_UNFOLLOW_URL
)


class PostsURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user_author = User.objects.create(
            username=AUTHOR_USERNAME,
            password=AUTHOR_PASSWORD
        )
        cls.user_other = User.objects.create(
            username=USER_USERNAME,
            password=USER_PASSWORD
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
        cls.POST_URL = reverse(
            'post',
            kwargs={'username': AUTHOR_USERNAME, 'post_id': cls.post.id}
        )
        cls.POST_EDIT_URL = reverse(
            'post_edit',
            kwargs={'username': AUTHOR_USERNAME, 'post_id': cls.post.id}
        )
        cls.POST_EDIT_NONE_AUTHENTICATE_REDIRECT = '{}?next={}'.format(
            LOGIN_URL,
            cls.POST_EDIT_URL
        )
        cls.ADD_COMMENT_URL = reverse(
            'add_comment',
            kwargs={'username': AUTHOR_USERNAME, 'post_id': cls.post.id}
        )
        cls.ADD_COMMENT_NONE_AUTHENTICATE_REDIRECT = '{}?next={}'.format(
            LOGIN_URL,
            cls.ADD_COMMENT_URL
        )

    def setUp(self):
        self.guest_client = Client()
        self.author_client = Client()
        self.author_client.force_login(self.user_author)
        self.other_client = Client()
        self.other_client.force_login(self.user_other)

    def test_urls_exist_at_desired_location(self):
        """URL-адреса доступны и отвечают ожидаемыми кодами"""
        urls_clients_codes = [
            [INDEX_URL, self.guest_client, 200],
            [GROUP_URL, self.guest_client, 200],
            [PROFILE_URL, self.guest_client, 200],
            [self.POST_URL, self.guest_client, 200],
            [NEW_POST_URL, self.guest_client, 302],
            [NEW_POST_URL, self.other_client, 200],
            [self.POST_EDIT_URL, self.guest_client, 302],
            [self.POST_EDIT_URL, self.other_client, 302],
            [self.POST_EDIT_URL, self.author_client, 200],
            [FOLLOW_INDEX, self.author_client, 200],
            [PROFILE_FOLLOW_URL, self.guest_client, 302],
            [PROFILE_FOLLOW_URL, self.author_client, 302],
            [PROFILE_UNFOLLOW_URL, self.guest_client, 302],
            [self.ADD_COMMENT_URL, self.guest_client, 302],
            [self.ADD_COMMENT_URL, self.author_client, 302],
            [WRONG_URL, self.guest_client, 404]
        ]
        for url, client, code in urls_clients_codes:
            with self.subTest(url=url, code=code):
                self.assertEqual(client.get(url).status_code, code)

    def test_create_and_modify_pages_redirect_anonymous(self):
        """URL-адреса перенаправляют на ожидаемые страницы"""
        urls_clients_destinations = [
            [
                NEW_POST_URL, self.guest_client,
                NEW_POST_REDIRECT
            ],
            [
                self.POST_EDIT_URL, self.guest_client,
                self.POST_EDIT_NONE_AUTHENTICATE_REDIRECT
            ],
            [
                self.ADD_COMMENT_URL, self.guest_client,
                self.ADD_COMMENT_NONE_AUTHENTICATE_REDIRECT
            ],
            [
                PROFILE_FOLLOW_URL, self.guest_client,
                PROFILE_FOLLOW_NONE_AUTHENTICATE_REDIRECT
            ],
            [
                PROFILE_UNFOLLOW_URL, self.guest_client,
                PROFILE_UNFOLLOW_NONE_AUTENTICATE_REDIRECT
            ],
            [
                self.POST_EDIT_URL, self.other_client,
                self.POST_URL
            ]
        ]
        for url, client, destination in urls_clients_destinations:
            with self.subTest(url=url, destination=destination):
                self.assertRedirects(client.get(url, follow=True), destination)

    def test_urls_uses_correct_template(self):
        """URL-адреса используют ожидаемые шаблоны."""
        templates_urls = [
            ['index.html', INDEX_URL],
            ['group.html', GROUP_URL],
            ['profile.html', PROFILE_URL],
            ['post.html', self.POST_URL],
            ['new_post.html', NEW_POST_URL],
            ['new_post.html', self.POST_EDIT_URL],
            ['follow.html', FOLLOW_INDEX],
            ['misc/404.html', WRONG_URL],
        ]
        for template, url in templates_urls:
            with self.subTest(tempalte=template, url=url):
                self.assertTemplateUsed(self.author_client.get(url), template)
