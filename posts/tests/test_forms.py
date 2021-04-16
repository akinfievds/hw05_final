import os
import shutil
import tempfile

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.forms import fields, models
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from posts.forms import PostForm
from posts.models import Comment, Group, Post, User

AUTHOR_USERNAME = 'Andrey'
AUTHOR_PASSWORD = 'qwerty'

GROUP_1_SLUG = 'test-slug'
GROUP_2_SLUG = 'test-slug-2'

INDEX_URL = reverse('index')
GROUP_1_URL = reverse('group', args=[GROUP_1_SLUG])
GROUP_2_URL = reverse('group', args=[GROUP_2_SLUG])
NEW_POST_URL = reverse('new_post')

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)

IMAGE_FILE = (
    b'\x47\x49\x46\x38\x39\x61\x02\x00'
    b'\x01\x00\x80\x00\x00\x00\x00\x00'
    b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
    b'\x00\x00\x00\x2C\x00\x00\x00\x00'
    b'\x02\x00\x01\x00\x00\x02\x02\x0C'
    b'\x0A\x00\x3B'
)

BROKEN_FILE = (
    b'\x47\x49\x46\x38\x39\x61\x02\x01'
    b'\x01\x00\x80\x00\x00\x00\x00\x02'
    b'\xFF\xFF\xFF\x21\xF9\x04\x00\x03'
    b'\x00\x00\x00\x2C\x00\x00\x00\x04'
    b'\x02\x00\x01\x00\x00\x02\x02\x0C'
    b'\x0A\x00\x3B'
)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(
            username=AUTHOR_USERNAME,
            password=AUTHOR_PASSWORD
        )
        cls.group_1 = Group.objects.create(
            title='Первое тестовое сообщество',
            description='Тестируем описание первой группы',
            slug=GROUP_1_SLUG
        )
        cls.group_2 = Group.objects.create(
            title='Второе тестовое сообщество',
            description='Тестируем описание второй группы',
            slug=GROUP_2_SLUG
        )
        cls.image = SimpleUploadedFile(
            name='small.gif',
            content=IMAGE_FILE,
            content_type='image/gif'
        )
        cls.broken_file = SimpleUploadedFile(
            name='broken_file.txt',
            content=BROKEN_FILE,
            content_type='text/plain'
        )
        cls.post = Post.objects.create(
            text='Тестируем тестовую заметку',
            author=cls.user
        )
        cls.form = PostForm()
        cls.POST_URL = reverse('post', args=[
            AUTHOR_USERNAME, cls.post.id])
        cls.POST_EDIT_URL = reverse('post_edit', args=[
            AUTHOR_USERNAME, cls.post.id])
        cls.ADD_COMMENT = reverse('add_comment', args=[
            AUTHOR_USERNAME, cls.post.id])

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def setUp(self):
        self.guest_client = Client()
        self.author = Client()
        self.author.force_login(self.user)

    def test_forms_shows_correct_context(self):
        """/new и /<username>/<post_id>/edit отображают ожидаемые данные"""
        urls = [NEW_POST_URL, self.POST_EDIT_URL]
        for url in urls:
            with self.subTest(url=url):
                response = self.author.get(url)
                form_field = response.context['form'].fields
                self.assertIsInstance(form_field['group'],
                                      models.ModelChoiceField)
                self.assertIsInstance(form_field['text'],
                                      fields.CharField)

    def test_new_post_creates_new_post(self):
        """/new форма создает новую заметку"""
        posts_count_before_adding = Post.objects.count()
        posts_id_before_adding = {post.id for post in Post.objects.all()}
        form_data = {
            'text': 'Тестируем создание заметки из формы',
            'group': self.group_1.id,
            'image': self.image,
        }
        response = self.author.post(NEW_POST_URL, data=form_data, follow=True)
        self.assertRedirects(response, INDEX_URL)
        self.assertEqual(Post.objects.count(), posts_count_before_adding + 1)
        posts_id_after_adding = {post.id for post in Post.objects.all()}
        new_post_id = list(posts_id_after_adding - posts_id_before_adding)
        self.assertEqual(len(new_post_id), 1)
        new_post = Post.objects.get(id=new_post_id[0])
        self.assertEqual(new_post.text, form_data['text'])
        self.assertEqual(new_post.group.id, form_data['group'])
        self.assertEqual(new_post.author, self.user)
        self.assertIn(
            os.path.relpath(new_post.image.name, start='posts'),
            os.listdir(os.path.join(settings.MEDIA_ROOT, 'posts'))
        )

    def test_new_post_decline_file_types(self):
        """/new форма выдает ошибку при загрузке не изображения"""
        posts_count_before_adding = Post.objects.count()
        form_data = {
            'text': 'Тестируем создание заметки с неправильным типов файла',
            'group': self.group_1.id,
            'image': self.broken_file
        }
        response = self.author.post(NEW_POST_URL, data=form_data, follow=True)
        error_message = (
            'Формат файлов \'txt\' не поддерживается. '
            'Поддерживаемые форматы файлов: \'bmp, dib, gif, '
            'tif, tiff, jfif, jpe, jpg, jpeg, pbm, pgm, ppm, '
            'pnm, png, apng, blp, bufr, cur, pcx, dcx, dds, ps, '
            'eps, fit, fits, fli, flc, ftc, ftu, gbr, grib, h5, '
            'hdf, jp2, j2k, jpc, jpf, jpx, j2c, icns, ico, im, '
            'iim, mpg, mpeg, mpo, msp, palm, pcd, pdf, pxr, psd, '
            'bw, rgb, rgba, sgi, ras, tga, icb, vda, vst, webp, '
            'wmf, emf, xbm, xpm\'.'
        )
        self.assertFormError(response, 'form', 'image', error_message)
        posts_count_after_adding = Post.objects.count()
        self.assertEqual(posts_count_before_adding, posts_count_after_adding)

    def test_add_comment_creates_new_comment(self):
        """username/post_id/comment форма создает новый комментарий"""
        comments_count_before_adding = Comment.objects.count()
        comments_id_before_adding = {comment.id for comment
                                     in Comment.objects.all()}
        form_data = {'text': 'Тестируем создание комментария из формы'}
        response = self.author.post(self.ADD_COMMENT, data=form_data,
                                    follow=True)
        self.assertRedirects(response, self.POST_URL)
        self.assertEqual(
            Comment.objects.count(),
            comments_count_before_adding + 1
        )
        comments_id_after_adding = {comment.id for comment
                                    in Comment.objects.all()}
        new_comment_id = list(
            comments_id_after_adding - comments_id_before_adding
        )
        self.assertEqual(len(new_comment_id), 1)
        new_comment = Comment.objects.get(id=new_comment_id[0])
        self.assertEqual(new_comment.text, form_data['text'])

    def test_post_edit_modifies_desired_post(self):
        """/<username>/<post_id>/edit/ изменяет соответствующую запись в БД"""
        post_count_before_modify = Post.objects.count()
        form_data = {
            'text': 'Тестируем редактирование тестовой заметки',
            'group': self.group_2.id
        }
        response = self.author.post(
            self.POST_EDIT_URL,
            data=form_data,
            follow=True
        )
        post_count_after_modify = Post.objects.count()
        self.assertRedirects(response, self.POST_URL)
        self.assertEqual(
            post_count_before_modify,
            post_count_after_modify
        )
        edited_post = response.context['post']
        self.assertEqual(edited_post.text, form_data['text'])
        self.assertEqual(edited_post.group.id, form_data['group'])
        self.assertEqual(edited_post.author, self.user)
