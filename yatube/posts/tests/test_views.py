from django import forms
from django.conf import settings
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from time import sleep

from posts.models import Group, Post

User = get_user_model()


class VievFunctionTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='Test_username')
        cls.user_author = User.objects.create_user(username='Test_author_name')
        cls.group = Group.objects.create(
            title='Тестовая_группа',
            slug='test_slug',
            description='Тестовое_описание',
        )
        cls.group_2 = Group.objects.create(
            title='Тестовая_группа_2',
            slug='test_slug_2',
            description='Тестовое_описание_2',
        )
        cls.small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=cls.small_gif,
            content_type='image/gif'
        )
        cls.COUNT_POST_FOR_TEST = 13
        for post_number in range(cls.COUNT_POST_FOR_TEST):
            sleep(0.01)
            cls.post = Post.objects.create(
                text=f'Test text пост номер {post_number+1}',
                author=cls.user_author,
                group=cls.group,
                image=cls.uploaded,
            )

    def setUp(self):
        cache.clear()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.authorized_client_author = Client()
        self.authorized_client_author.force_login(
            self.user_author)

    def checking_context(self, response, bool_var=False):
        if bool_var is True:
            object = response.context['page_obj']
        else:
            object = response.context['page_obj'][0]
        self.assertEqual(object.author, self.user_author)
        self.assertEqual(object.text, 'Test text пост номер 13')
        self.assertEqual(object.group, self.group)
        self.assertEqual(object.pub_date, self.post.pub_date)
        self.assertEqual(object.image, self.post.image)

    # def test_pages_uses_correct_template(self):
    #     templates_pages_names_list = (
    #         # ('posts:index', None, 'posts/index.html'),
    #         ('posts:group_posts', (
    #             self.group.slug,), 'posts/group_list.html'),
    #         # ('posts:profile', (
    #         #     self.post.author.username,), 'posts/profile.html'),
    #         ('posts:post_detail', (self.post.id,), 'posts/post_detail.html'),
    #         ('posts:post_create', None, 'posts/create_post.html'),
    #         ('posts:post_edit', (self.post.id,), 'posts/create_post.html'),
    #     )
    #     for address, args, template in templates_pages_names_list:
    #         with self.subTest(address=address):
    #             response = self.authorized_client_author.get(
    #                 reverse(address, args=args))
    #             self.assertTemplateUsed(response, template)
    # обнаружил что полностью аналогичный тест написан в test_urls

    def test_pages_accept_correct_context_index(self):
        """проверка правильности передаваемого
        словаря context функции index."""
        response = self.authorized_client.get(reverse('posts:index'))
        self.checking_context(response)

    def test_pages_accept_correct_context_post_detail(self):
        response = self.authorized_client.get(
            reverse('posts:post_detail', args=(self.post.id,)))
        self.checking_context(response, bool_var=True)

    def test_pages_accept_correct_context_group_post(self):
        """проверка правильности передаваемого
        словаря context функции group_posts."""
        response = self.authorized_client.get(reverse(
            'posts:group_posts', args=(self.group.slug,)))
        self.checking_context(response)
        second_object = response.context['group']
        self.assertEqual(second_object.slug, 'test_slug')
        self.assertEqual(second_object.title, 'Тестовая_группа')
        self.assertEqual(second_object.description, 'Тестовое_описание')

    def test_pages_accept_correct_context_profile(self):
        """проверка правильности передаваемого
        словаря context функции profile."""
        response = self.authorized_client.get(
            reverse('posts:profile', args=(self.user_author.username,)))
        self.checking_context(response)
        object_2 = response.context['author']
        object_3 = response.context['count_post_author']
        self.assertEqual(object_2, self.post.author)
        self.assertEqual(object_3, self.COUNT_POST_FOR_TEST)

    def test_pages_accept_correct_context_post_create_and_edit(self):
        """проверка правильности передаваемого
        словаря context функции poct_create and post_edit."""
        form_filds = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        tuple = (
            ('posts:post_create', None,),
            ('posts:post_edit', (self.post.id,),),
        )
        for address, args in tuple:
            with self.subTest(address=address):
                response = self.authorized_client_author.post(
                    reverse(address, args=args))
                for value, expected in form_filds.items():
                    with self.subTest(value=value):
                        object = response.context.get(
                            'form').fields.get(value)
                self.assertIsInstance(object, expected)

    def test_pagonator(self):
        pages_list = (
            (reverse('posts:index', None,)),
            (reverse('posts:group_posts', args=(self.group.slug,))),
            (reverse('posts:profile', args=(self.post.author,))),
        )
        for page in pages_list:
            with self.subTest(page=page):
                response = self.authorized_client_author.get(page)
                self.assertEqual(len(response.context['page_obj']), (
                    settings.COUNT_POSTS))
                response_2 = self.authorized_client.get(page + '?page=2')
                self.assertEqual(len(response_2.context['page_obj']), (
                    self.COUNT_POST_FOR_TEST - settings.COUNT_POSTS))
