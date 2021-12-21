from http import HTTPStatus

from django.test import Client, TestCase
from django.urls import reverse


class StaticURLTests(TestCase):
    AUTHOR_REVERSE_URL = reverse('about:author')
    TECH_REVERSE_URL = reverse('about:tech')
    AUTHOR_URL = '/about/author/'
    TECH_URL = '/about/tech/'

    def setUp(self):
        self.guest_client = Client()

    def test_author(self):
        """Страница /about/author/ доступна любому пользователю."""
        response = self.guest_client.get(self.AUTHOR_REVERSE_URL)
        self.assertEqual(response.status_code, HTTPStatus.OK,
                         'Страница об авторе не доступна')

    def test_tech(self):
        """Страница /about/tech/ доступна любому пользователю."""
        response = self.guest_client.get(self.TECH_REVERSE_URL)
        self.assertEqual(response.status_code, HTTPStatus.OK,
                         'Страница о технологиях не доступна')

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        link_URLs_n_templates = {
            self.AUTHOR_URL: 'about/author.html',
            self.TECH_URL: 'about/tech.html',
        }
        for adress, template in link_URLs_n_templates.items():
            with self.subTest(adress=adress):
                response = self.guest_client.get(adress)
                self.assertTemplateUsed(response, template)
