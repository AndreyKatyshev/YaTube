from http import HTTPStatus
from django.contrib.auth import get_user_model, REDIRECT_FIELD_NAME
from django.core.cache import cache
from django.test import Client, TestCase
from django.urls import reverse


from posts.models import Group, Post

User = get_user_model()


class StaticURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='TestNameNoAuthor')
        cls.user_author = User.objects.create_user(username='TestAuthor')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user_author,
            text='Тестовый пост'
        )

    def setUp(self):
        cache.clear()
        self.authorized_client_no_author = Client()
        self.authorized_client_no_author.force_login(self.user)
        self.authorized_client_author = Client()
        self.authorized_client_author.force_login(self.user_author)

        self.general_tuple = (
            ('posts:index', None, '/'),
            ('posts:group_posts', (
                self.group.slug,), f'/group/{self.group.slug}/'),
            ('posts:profile', (
                self.user_author.username,),
                f'/profile/{self.user_author.username}/'),
            ('posts:post_detail', (
                self.post.id,), f'/posts/{self.post.id}/'),
            ('posts:post_create', None, '/create/'),
            ('posts:post_edit', (
                self.post.id,), f'/posts/{self.post.id}/edit/'),
            ('posts:follow_index', None, '/follow/',),
            ('posts:profile_follow', (
                self.user_author.username,),
                f'/profile/{self.user_author.username}/follow/',),
            ('posts:profile_unfollow', (
                self.user_author.username,),
                f'/profile/{self.user_author.username}/unfollow/',),
            ('posts:add_comment', (
                self.post.id,), f'/posts/{self.post.id}/comment/'),
        )

    def test_reverse(self):
        """Проверяет соответствие реверсов и хардюрлов."""
        for address, args, hard_url in self.general_tuple:
            with self.subTest(address=address):
                self.assertEqual(reverse(address, args=args), hard_url)

    def test_available_guest(self):
        """Тестирует доступность страниц неавторизованному
        пользоветелю и переадресацию на другие страницы
        в случае недоступности запрашиваемых."""
        for address, args, hard_url in self.general_tuple:
            with self.subTest(address=address):
                redirect_login = reverse('users:login')
                response = self.client.get(
                    hard_url, args=args, follow=True)
                if address in ['posts:post_create', 'posts:post_edit']:
                    reverse_var = reverse(address, args=args)
                    target_url = (
                        f'{redirect_login}?{REDIRECT_FIELD_NAME}={reverse_var}'
                    )
                    self.assertRedirects(
                        response, target_url)
                else:
                    self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_available_authorized_user(self):
        """Проверяет доступность страниц авторизованному
        пользоветелю и редирект с недоступных."""
        for address, args, hard_url in self.general_tuple:
            with self.subTest(address=address):
                response = self.authorized_client_no_author.get(
                    hard_url, args=args)
                if address in ['posts:post_edit']:
                    self.assertRedirects(response, reverse(
                        'posts:post_detail', args=args))
                elif address in [
                    'posts:profile_follow',
                    'posts:profile_unfollow',
                ]:
                    self.assertRedirects(response, reverse(
                        'posts:profile', args=args))
                elif address == 'posts:add_comment':
                    self.assertRedirects(response, reverse(
                        'posts:post_detail', args=args))
                else:
                    self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_available_author(self):
        """Проверяет доступность страниц автору поста."""
        for address, args, hard_url in self.general_tuple:
            with self.subTest(address=address):
                response = self.authorized_client_author.get(
                    hard_url, args=args)
                if address in [
                    'posts:profile_follow',
                    'posts:profile_unfollow',
                ]:
                    self.assertRedirects(response, reverse(
                        'posts:profile', args=args))
                elif address == 'posts:add_comment':
                    self.assertRedirects(response, reverse(
                        'posts:post_detail', args=args))
                else:
                    self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_unexisting_url(self):
        """Проверка на переход по несуществующему адресу
        и использования кастомного шаблона страницы 404."""
        response = self.authorized_client_author.get('/bad_url/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertTemplateUsed(response, 'core/404.html')

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = (
            ('posts:index', None, 'posts/index.html'),
            ('posts:group_posts', (
                self.group.slug,), 'posts/group_list.html'),
            ('posts:profile', (
                self.post.author.username,), 'posts/profile.html'),
            ('posts:post_detail', (
                self.post.id,), 'posts/post_detail.html'),
            ('posts:post_create', None, 'posts/create_post.html'),
            ('posts:post_edit', (
                self.post.id,), 'posts/create_post.html'),
            ('posts:follow_index', None, 'posts/follow.html'),
        )
        for address, args, template in templates_url_names:
            with self.subTest(address=address):
                response = self.authorized_client_author.get(
                    reverse(address, args=args))
                self.assertTemplateUsed(response, template)
