from http import HTTPStatus
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

User = get_user_model()


class StaticURLTests(TestCase):

    def test_url_about(self):
        """Проверяет правильное использование шаблонов
        и доступность страниц любому пользователю
        """
        dictionary_url_address = (
            ('about:author', None, 'about/author.html',),
            ('about:tech', None, 'about/tech.html',),
        )
        for address, args, template in dictionary_url_address:
            with self.subTest(address=address):
                response = self.client.get(reverse(address, args=args))
                self.assertTemplateUsed(response, template)
                self.assertEqual(response.status_code, HTTPStatus.OK)
