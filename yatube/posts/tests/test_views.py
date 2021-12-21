import shutil
import tempfile

from django import forms
from django.conf import settings
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from ..models import Follow, Group, Post, User

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostViewsTest(TestCase):
    @classmethod
    def setUpClass(self):
        super().setUpClass()
        self.user = User.objects.create_user(username='auth')
        self.second_user = User.objects.create_user(username='leo')
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
        self.POST_DETAIL_URL = reverse(
            'post:post_detail', kwargs={'post_id': self.post.id})
        self.POST_EDIT_URL = reverse(
            'post:post_edit', kwargs={'post_id': self.post.id})

    INDEX_URL = reverse('post:index')
    FOLLOW_INDEX_URL = reverse('post:follow_index')
    GROUP_LIST_URL = reverse('post:group_list',
                             kwargs={'SlugField': 'testslug'})
    USERNAME_URL = reverse('post:profile',
                           kwargs={'username': 'auth'})
    USERNAME2_URL = reverse('post:profile',
                            kwargs={'username': 'leo'})
    POST_CREATE_URL = reverse('post:post_create')

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.second_authorized_client = Client()
        self.second_authorized_client.force_login(self.second_user)

    def test_names_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        link_names_n_templates = {
            self.INDEX_URL: 'posts/index.html',
            self.GROUP_LIST_URL: 'posts/group_list.html',
            self.USERNAME_URL: 'posts/profile.html',
            self.POST_DETAIL_URL: 'posts/post_detail.html',
            self.POST_EDIT_URL: 'posts/create_post.html',
            self.POST_CREATE_URL: 'posts/create_post.html',
        }
        for adress, template in link_names_n_templates.items():
            with self.subTest(adress=adress):
                response = self.authorized_client.get(adress)
                self.assertTemplateUsed(response, template)

    def test_paginator_n_context_4_pages_with_posts_list(self):
        """проверяем пагинатор и содержимое на страницах со списком статей"""
        link_names = (
            self.INDEX_URL,
            self.GROUP_LIST_URL,
            self.USERNAME_URL,
        )
        test_dic = {
            'text': 'Тест, тест, тест',
            'group.title': 'Тестовая группа',
            'group.slug': 'testslug',
            'author.username': 'auth',
        }
        for name in link_names:
            with self.subTest(name=name):
                response = self.authorized_client.get(name)
                first_post = response.context.get('page_obj')[0]
                post_group = response.context.get('group')
                post_author = response.context.get('username')

                self.assertEqual(len(
                    response.context['page_obj']), 10, 'неверное количество '
                    + f'постов на первой странице {name}')
                response = self.authorized_client.get(name + '?page=2')
                self.assertEqual(len(
                    response.context['page_obj']), 5, 'неверное количество '
                    + f'постов на второй странице {name}')

                self.assertEqual(test_dic['text'],
                                 first_post.text,
                                 f'текст статьи на {name} не соответствует '
                                 + 'передаваемому')
                self.assertEqual(test_dic['group.title'],
                                 first_post.group.title,
                                 f'группа статьи на {name} не соответствует '
                                 + 'передаваемой')
                self.assertEqual(test_dic['author.username'],
                                 first_post.author.username,
                                 f'автор статьи на {name} не соответствует '
                                 + 'передаваемому')

                if name == '/group/testslug/':
                    self.assertEqual(test_dic['group.slug'],
                                     post_group.slug,
                                     f'ошибка фильтра по группе на {name}')

                if name == '/group/auth/':
                    self.assertEqual(test_dic['author.username'],
                                     post_author.username,
                                     f'ошибка фильтра по автору на {name}')

    def test_post_detail_show_correct_context(self):
        """проверяем post_detail на соответствие id, правильности context"""
        response = self.authorized_client.get(self.POST_DETAIL_URL)
        guest_response = self.guest_client.get(self.POST_DETAIL_URL)
        second_authorized_response = self.second_authorized_client.get(
            self.POST_DETAIL_URL)

        self.assertEqual(
            response.context['post'].id, 15, 'вызван не тот пост')

        self.assertEqual(
            response.context['post'].text,
            'Тест, тест, тест', 'передаётся не тот текст статьи')

        self.assertEqual(
            response.context['title'],
            response.context['post'].text[:30],
            'передаётся не правильный заголовок')

        self.assertEqual(
            response.context['posts_count'],
            15, 'передаётся не правильное количество статей')

        self.assertFalse(
            guest_response.context['is_edit'],
            'передаётся не правильный флаг редактирования')

        self.assertFalse(
            second_authorized_response.context['is_edit'],
            'передаётся не правильный флаг редактирования')

    def test_post_edit_show_correct_context(self):
        """проверяем post_edit на id, правильность context и формы"""
        response = self.authorized_client.get(self.POST_EDIT_URL)
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        form_values = {
            'text': 'Тест, тест, тест',
            'group': 1,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                text_field = response.context.get('form').initial[value]
                self.assertIsInstance(form_field, expected, f'поле {value} '
                                      + 'не того типа')

                self.assertEqual(text_field, form_values[value],
                                 'передаётся не тот текст формы')

                self.assertTrue(response.context['is_edit'],
                                'передаётся не правильный флаг редактирования')

    def test_post_create_show_correct_context(self):
        """проверяем post_create на правильность формы"""
        response = self.authorized_client.get(self.POST_CREATE_URL)
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }

        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected, f'поле {value} '
                                      + 'не того типа')
        self.assertFalse(response.context['is_edit'],
                         'передаётся не правильный флаг редактирования')

    def test_new_record_add_2_index_group_n_profile(self):
        """Тестирование отображения новой записи"""
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )

        self.new_group = Group.objects.create(
            title='Новая группа',
            slug='newslug',
            description='Ещё тест',
        )

        self.new_post = Post.objects.create(
            author=self.second_user,
            text='Тестирование отображения новой записи',
            group=self.new_group,
            image=uploaded
        )

        link_names = (
            self.INDEX_URL,
            reverse('post:group_list',
                    kwargs={'SlugField': self.new_group.slug}),
            reverse('post:profile',
                    kwargs={'username': self.second_user}),
        )
        test_dic = {
            'text': 'Тестирование отображения новой записи',
            'group.title': 'Новая группа',
            'group.slug': 'newslug',
            'author.username': 'leo',
            'image': uploaded
        }

        for name in link_names:
            with self.subTest(name=name):
                response = self.second_authorized_client.get(name)
                first_post = response.context.get('page_obj')[0]
                post_group = response.context.get('group')
                post_author = response.context.get('username')

                self.assertEqual(test_dic['text'],
                                 first_post.text,
                                 f'текст статьи на {name} не соответствует '
                                 + 'передаваемому')
                self.assertEqual(test_dic['group.title'],
                                 first_post.group.title,
                                 f'группа статьи на {name} не соответствует '
                                 + 'передаваемой')
                self.assertEqual(test_dic['author.username'],
                                 first_post.author.username,
                                 f'автор статьи на {name} не соответствует '
                                 + 'передаваемому')
                self.assertTrue(first_post.image is not None,
                                f'картинка на {name} не передаётся ')

                if name == '/group/newslug/':
                    self.assertEqual(test_dic['group.slug'],
                                     post_group.slug,
                                     f'ошибка фильтра по группе на {name}')

                if name == '/group/leo/':
                    self.assertEqual(test_dic['author.username'],
                                     post_author.username,
                                     f'ошибка фильтра по автору на {name}')

    def test_cached_index(self):
        """Тестирование кэширования главной"""
        text = 'Тестирование отображения новой записи'
        self.new_group = Group.objects.create(
            title='Новая группа',
            slug='newslug',
            description='Ещё тест',
        )

        self.new_post = Post.objects.create(
            author=self.second_user,
            text=text,
            group=self.new_group,
        )
        cache.clear()
        response = self.second_authorized_client.get(self.INDEX_URL)
        self.assertContains(response, text)

        Post.objects.filter(group=self.new_group).delete()
        response = self.second_authorized_client.get(self.INDEX_URL)
        self.assertContains(response, text)

        cache.clear()
        response = self.second_authorized_client.get(self.INDEX_URL)
        self.assertNotContains(response, text)

    def test_follow_index(self):
        """Тестирование отображения подписок"""
        text = 'Тестирование отображения подписки'
        self.new_group = Group.objects.create(
            title='Новая группа',
            slug='newslug',
            description='Ещё тест',
        )

        auth_response = self.authorized_client.get(self.USERNAME_URL)
        auth_len = len(auth_response.context.get('page_obj'))
        user_response = (
            self.second_authorized_client.get(self.USERNAME2_URL))
        user_len = len(user_response.context.get('page_obj'))
        self.new_post = Post.objects.create(
            author=self.second_user,
            text=text,
            group=self.new_group,
        )
        self.new_follow = Follow.objects.create(
            author_id=self.user.id,
            user_id=self.second_user.id,
        )
        cache.clear()

        auth_response = self.authorized_client.get(self.FOLLOW_INDEX_URL)
        auth_get_posts = auth_response.context.get('page_obj')
        user_response = (
            self.second_authorized_client.get(self.FOLLOW_INDEX_URL))
        user_get_posts = user_response.context.get('page_obj')

        self.assertEqual(user_len,
                         len(auth_get_posts),
                         'ошибка статья появилась в подписках ')
        self.assertEqual(auth_len,
                         len(user_get_posts),
                         'статья не появилась в подписках ')

    def test_auth_user_subscribe_and_unsubscribe(self):
        """Авторизованный пользователь  подписывется и
        отписывается от других пользователей.
        """
        text = 'Тестирование отображения новой записи'
        self.new_group = Group.objects.create(
            title='Новая группа',
            slug='newslug',
            description='Ещё тест',
        )

        self.new_post = Post.objects.create(
            author=self.second_user,
            text=text,
            group=self.new_group,
        )
        cache.clear()
        null_following = self.second_user.following.count()
        self.assertEqual(0, null_following)
        self.authorized_client.get(reverse(
            'post:profile_follow',
            kwargs={'username': self.second_user.username}
        ))
        self.assertEqual(
            self.second_user.following.count(),
            null_following + 1
        )
        self.assertTrue(
            self.user.follower.filter(
                author_id=self.second_user.id
            ).exists()
        )
        self.authorized_client.get(
            reverse(
                'post:profile_unfollow',
                kwargs={'username': self.second_user.username}
            )
        )
        self.assertEqual(
            self.second_user.following.count(),
            null_following
        )
