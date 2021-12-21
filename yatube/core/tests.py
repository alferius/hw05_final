from http import HTTPStatus

from django.test import TestCase


class ViewTestClass(TestCase):
    def test_error404_page(self):
        response = self.client.get('/nonexist-page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND,
                         'внезапно стала доступна страница unknown')

        self.assertTemplateUsed(response, 'core/404.html')
