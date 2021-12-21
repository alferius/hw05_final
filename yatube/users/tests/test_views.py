from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post, User


class UsersViewsTest(TestCase):
    USER_LOGOUT_URL = reverse('users:logout')
    USER_SIGNUP_URL = reverse('users:signup')
    USER_LOGIN_URL = reverse('users:login')
    USER_PASSWORD_RESET_URL = reverse('users:password_reset')
    USER_PASSWORD_RESET_DONE_URL = reverse('users:password_reset_done')
    USER_PASSWORD_RESET_COMPLETE_URL = reverse('users:password_reset_complete')
    USER_PASSWORD_CHANGE_URL = reverse('users:password_change')
    USER_PASSWORD_CHANGE_DONE_URL = reverse('users:password_change_done')

    @classmethod
    def setUpClass(self):
        super().setUpClass()
        self.user = User.objects.create_user(username='auth')
        self.group = Group.objects.create(
            title='Тестовая группа',
            slug='testslug',
            description='Для тестов',
        )
        for _ in range(15):
            self.post = Post.objects.create(
                author=self.user,
                text='Тест, тест, тест',
                group=self.group,
            )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_names_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        link_names_n_templates = {
            self.USER_LOGOUT_URL: 'users/logged_out.html',
            self.USER_SIGNUP_URL: 'users/signup.html',
            self.USER_LOGIN_URL: 'users/login.html',
            self.USER_PASSWORD_RESET_URL: 'users/password_reset_form.html',
            self.USER_PASSWORD_RESET_DONE_URL:
                'users/password_reset_done.html',
            self.USER_PASSWORD_RESET_COMPLETE_URL:
                'users/password_reset_complete.html',
            self.USER_PASSWORD_CHANGE_URL:
                'users/password_change_form.html',
            self.USER_PASSWORD_CHANGE_DONE_URL:
                'users/password_change_done.html',
        }

        for adress, template in link_names_n_templates.items():
            with self.subTest(adress=adress):
                self.authorized_client.force_login(self.user)
                response = self.authorized_client.get(adress)
                self.assertTemplateUsed(response, template)
