from http import HTTPStatus

from django.test import Client, TestCase

from posts.models import User


class usersURLTest(TestCase):
    USER_LOGOUT_URL = '/auth/logout/'
    USER_SIGNUP_URL = '/auth/signup/'
    USER_LOGIN_URL = '/auth/login/'
    USER_PASSWORD_RESET_URL = '/auth/password_reset/'
    USER_PASSWORD_RESET_DONE_URL = '/auth/password_reset/done/'
    USER_PASSWORD_RESET_COMPLETE_URL = '/auth/reset/done/'
    USER_PASSWORD_CHANGE_URL = '/auth/password_change/'
    USER_PASSWORD_CHANGE_REDIRECT_URL = ('/auth/login/?next=/auth/'
                                         + 'password_change/')
    USER_PASSWORD_CHANGE_DONE_URL = '/auth/password_change/done/'
    USER_PASSWORD_CHANGE_DONE_REDIRECT_URL = ('/auth/login/?next=/auth/'
                                              + 'password_change/done/')

    @classmethod
    def setUpClass(self):
        super().setUpClass()
        self.user = User.objects.create_user(username='auth')

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_access_for_all(self):
        """Доступ неавторизированного пользователя к страницам users"""
        pages_4_all = (self.USER_LOGOUT_URL, self.USER_SIGNUP_URL,
                       self.USER_LOGIN_URL, self.USER_PASSWORD_RESET_URL,
                       self.USER_PASSWORD_RESET_DONE_URL)
        for page in pages_4_all:
            with self.subTest(page=page):
                response = self.guest_client.get(page)
                self.assertEqual(response.status_code, HTTPStatus.OK,
                                 f'недоступна страница {page}')

        response = self.guest_client.get(self.USER_PASSWORD_CHANGE_URL,
                                         follow=True)
        self.assertRedirects(
            response, self.USER_PASSWORD_CHANGE_REDIRECT_URL
        )

        response = self.guest_client.get(self.USER_PASSWORD_CHANGE_DONE_URL,
                                         follow=True)
        self.assertRedirects(
            response, self.USER_PASSWORD_CHANGE_DONE_REDIRECT_URL
        )

    def test_access_for_autorized(self):
        """Доступ авторизированного пользователя к страницам users"""
        response = self.authorized_client.get(self.USER_PASSWORD_CHANGE_URL)
        self.assertEqual(response.status_code,
                         HTTPStatus.OK,
                         'страница password_change недоступна '
                         + 'авторизированному пользователю')
        self.assertTemplateUsed(response, 'users/password_change_form.html')

        response = self.authorized_client.get(
            self.USER_PASSWORD_CHANGE_DONE_URL)
        self.assertEqual(response.status_code,
                         HTTPStatus.OK,
                         'страница уведомления об изменении пароля недоступна '
                         + 'автору')
        self.assertTemplateUsed(response, 'users/password_change_done.html')

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        link_URLs_n_templates = {
            self.USER_LOGOUT_URL: 'users/logged_out.html',
            self.USER_SIGNUP_URL: 'users/signup.html',
            self.USER_LOGIN_URL: 'users/login.html',
            self.USER_PASSWORD_RESET_URL: 'users/password_reset_form.html',
            self.USER_PASSWORD_RESET_DONE_URL:
                'users/password_reset_done.html',
            self.USER_PASSWORD_RESET_COMPLETE_URL:
                'users/password_reset_complete.html',
        }
        for adress, template in link_URLs_n_templates.items():
            with self.subTest(adress=adress):
                response = self.authorized_client.get(adress)
                self.assertTemplateUsed(response, template)
