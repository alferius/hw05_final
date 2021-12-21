import shutil
import tempfile

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from ..models import Comment, Group, Post, User

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostFormTest(TestCase):

    @classmethod
    def setUpClass(self):
        super().setUpClass()
        self.user = User.objects.create_user(username='auth')
        self.group = Group.objects.create(
            title='Тестовая группа',
            slug='testslug',
            description='Для тестов',
        )
        self.post = Post.objects.create(
            author=self.user,
            text='Тест, тест, тест',
            group=self.group,
        )
        self.POST_EDIT_URL = reverse(
            'post:post_edit', kwargs={'post_id': self.post.id})
        self.COMMENT_URL = f'/posts/{self.post.id}/comment'
        self.POST_DETAIL_URL = '/posts/' + str(self.post.id) + '/'

    POST_CREATE_URL = reverse('post:post_create')
    USERNAME_URL = reverse('post:profile',
                           kwargs={'username': 'auth'})

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_post(self):
        """Валидная форма создает запись в Post."""
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
        posts_count = Post.objects.count()
        test_dic = {
            'text': 'Ещё один тест',
            'group_id': self.group.id,
            'author_id': self.user.id,
            'image': uploaded,
        }
        response = self.authorized_client.post(
            self.POST_CREATE_URL,
            data=test_dic,
            follow=True
        )
        self.assertRedirects(response, self.USERNAME_URL)
        self.assertEqual(Post.objects.count(), posts_count + 1)

    def test_edit_post(self):
        """Валидная форма изменяет запись в Post."""
        response = self.authorized_client.get(self.POST_EDIT_URL)
        old_post_text = response.context.get('form').initial['text']
        test_dic = {
            'text': 'Ещё один тест',
            'group_id': self.group.id,
            'author_id': self.user.id
        }
        response = self.authorized_client.post(
            self.POST_EDIT_URL,
            data=test_dic,
            follow=True
        )
        response = self.authorized_client.get(self.POST_EDIT_URL)
        new_post_text = response.context.get('form').initial['text']
        self.assertNotEqual(old_post_text, new_post_text)

    def test_create_comment(self):
        comments_count = Comment.objects.count()
        comment_dic = {
            'text': 'Зашибановский комментарий',
            'post': self.post.id,
            'author_id': self.user.id,
        }
        response = self.authorized_client.post(
            self.COMMENT_URL,
            data=comment_dic,
            follow=True
        )
        self.assertRedirects(response, self.POST_DETAIL_URL)
        self.assertEqual(Comment.objects.count(), comments_count + 1)
