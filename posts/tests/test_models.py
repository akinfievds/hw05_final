from django.test import TestCase

from posts.models import Group

USER_USERNAME = 'Andrey'
USER_PASSWORD = 'qwerty'

GROUP_TITLE = 'Тестовое название'
POST_TEXT = 'Тестовый текст, Тестовый текст, Тестовый текст'


class GroupModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title=GROUP_TITLE,
        )

    def test_title_label(self):
        """verbose_name поля title совпадает с ожидаемым."""
        verbose = Group._meta.get_field('title').verbose_name
        self.assertEquals(verbose, 'Название')

    def test_object_str_name(self):
        """___str___ модели Post совпадает с ожидаемым """
        self.assertEquals(GROUP_TITLE, str(self.group))
