from http import HTTPStatus

from django.test import Client, TestCase

from ..models import Group, Post, User


class PostURLTest(TestCase):
    INDEX_URL = '/'
    GROUP_LIST_URL = '/group/testslug/'
    USER_URL = '/profile/auth/'
    POST_CREATE_URL = '/create/'
    UNKNOWN_URL = '/unknown/'
    CREATE_REDIRECT_URL = '/auth/login/?next=/create/'

    @classmethod
    def setUpClass(self):
        super().setUpClass()
        # автор тестовой записи
        self.user = User.objects.create_user(username='auth')
        # просто зарегистрированный пользователь
        self.second_user = User.objects.create_user(username='leo')
        self.group = Group.objects.create(
            title='Тестовая группа',
            slug='testslug',
            description='Для тестов',
        )
        self.post = Post.objects.create(
            author=self.user,
            text='Тест, тест, тест',
        )
        self.POST_DETAIL_URL = '/posts/' + str(self.post.id) + '/'
        self.POST_EDIT_URL = '/posts/' + str(self.post.id) + '/edit/'
        self.EDIT_REDIRECT_URL = ('/auth/login/?next='
                                  + f'/posts/{self.post.id}/edit/')
        self.COMMENT_URL = f'/posts/{self.post.id}/comment'
        self.COMMENT_REDIRECT_URL = ('/auth/login/?next='
                                     + f'/posts/{self.post.id}/comment')

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_second_client = Client()
        self.authorized_client.force_login(self.user)
        self.authorized_second_client.force_login(self.second_user)

    def test_access_for_all(self):
        """Доступ неавторизированного пользователя к страницам"""
        pages_4_all = (self.INDEX_URL, self.GROUP_LIST_URL, self.USER_URL,
                       self.POST_DETAIL_URL,)
        for page in pages_4_all:
            with self.subTest(page=page):
                response = self.guest_client.get(page)
                self.assertEqual(response.status_code, HTTPStatus.OK,
                                 f'недоступна страница {page}')

        response = self.guest_client.get(self.UNKNOWN_URL)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND,
                         'внезапно стала доступна страница unknown')

        response = self.guest_client.get(self.POST_CREATE_URL, follow=True)
        self.assertRedirects(
            response, self.CREATE_REDIRECT_URL
        )

        response = self.guest_client.get(self.COMMENT_URL, follow=True)
        self.assertRedirects(
            response, self.COMMENT_REDIRECT_URL
        )

        response = self.guest_client.get(self.POST_EDIT_URL, follow=True)
        self.assertRedirects(
            response, self.EDIT_REDIRECT_URL
        )

    def test_access_for_autorized(self):
        """Доступ авторизированного пользователя к страницам"""
        response = self.authorized_client.get(self.POST_CREATE_URL)
        self.assertEqual(response.status_code,
                         HTTPStatus.OK,
                         'страница create недоступна '
                         + 'авторизированному пользователю')

        response = self.authorized_client.get(self.POST_EDIT_URL)
        self.assertEqual(response.status_code,
                         HTTPStatus.OK,
                         'страница редактирования недоступна автору')

        response = self.authorized_second_client.get(self.POST_EDIT_URL,
                                                     follow=True)
        self.assertRedirects(response, self.POST_DETAIL_URL)

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        link_URLs_n_templates = {
            self.INDEX_URL: 'posts/index.html',
            self.POST_DETAIL_URL: 'posts/post_detail.html',
            self.POST_EDIT_URL: 'posts/create_post.html',
            self.POST_CREATE_URL: 'posts/create_post.html',
            self.GROUP_LIST_URL: 'posts/group_list.html',
            self.USER_URL: 'posts/profile.html',
        }
        for adress, template in link_URLs_n_templates.items():
            with self.subTest(adress=adress):
                response = self.authorized_client.get(adress)
                self.assertTemplateUsed(response, template)
