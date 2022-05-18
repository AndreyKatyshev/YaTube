from django.contrib.auth import get_user_model
from django.test import TestCase

from posts.models import Group, Post

User = get_user_model()


class ModelsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Test_slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост'
        )

    def test_models_have_corretc_str_group_and_post(self):
        dict = {
            self.group: self.group.title,
            self.post: self.post.text[0:15],
        }
        for object, expected_values in dict.items():
            with self.subTest(object=object):
                check = str(object)
                self.assertEqual(check, expected_values)

    def test_verbose_name_post(self):
        """verbose_name в полях совпадает с ожидаемым."""
        post = self.post
        field_verboses = {
            'text': 'Текст записи',
            'pub_date': 'Дата публикации',
            'author': 'Автор',
        }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    post._meta.get_field(field).verbose_name, expected_value)

    def test_verbose_name_group(self):
        """verbose_name в полях совпадает с ожидаемым."""
        group = self.group
        field_verboses = {
            'title': 'Название сообщества',
            'slug': 'Уникальный слаг',
            'description': 'Описание',
        }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    group._meta.get_field(field).verbose_name, expected_value)

    def test_help_text_post(self):
        """help_text в полях совпадает с ожидаемым."""
        post = self.post
        field_verboses = {
            'text': 'Введите сюда то чем хотите поделиться с миром',
            'group': 'выбирите группу, но это не обязательно',
        }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    post._meta.get_field(field).help_text, expected_value)
