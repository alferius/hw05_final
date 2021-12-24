from django.test import TestCase

from ..models import Comment, Follow, Group, Post, User


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.second_user = User.objects.create_user(username='user')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='testslug',
            description='Для тестов',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тест, тест, тест',
        )
        cls.comment = Comment.objects.create(
            post=cls.post,
            author=cls.second_user,
            text='this is a comment'
        )
        cls.follow = Follow.objects.create(
            user=cls.second_user,
            author=cls.user
        )

    def test_models_have_correct_object_names(self):
        """Проверяем, что у моделей корректно работает __str__."""
        models = (PostModelTest.post, PostModelTest.group,
                  PostModelTest.comment, PostModelTest.follow)
        for val in models:
            with self.subTest(val=val):
                if val == PostModelTest.group:
                    self.assertEqual(
                        str(val),
                        val.title)
                elif val == PostModelTest.follow:
                    self.assertEqual(
                        str(val),
                        val.user.username)
                else:
                    self.assertEqual(
                        str(val),
                        val.text[:15])

    def test_post_field_have_title_label(self):
        test_post = PostModelTest.post
        field_verboses = {
            'text': 'Текст поста',
            'pub_date': 'Дата публикации',
            'author': 'Автор',
            'group': 'Группа',
        }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    test_post._meta.get_field(field).verbose_name,
                    expected_value)

    def test_follow_field_have_title_label(self):
        test_follow = PostModelTest.follow
        field_verboses = {
            'author': 'Автор',
            'user': 'Пользователь',
        }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    test_follow._meta.get_field(field).verbose_name,
                    expected_value)

    def test_post_field_have_help_text(self):
        """проверяем вспомогательные поля"""
        test_post = PostModelTest.post
        field_verboses = {
            'text': 'Введите текст поста',
            'group': 'Выберите группу',
        }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    test_post._meta.get_field(field).help_text,
                    expected_value)

    def test_comment_field_have_help_text(self):
        """проверяем вспомогательные поля"""
        test_comment = PostModelTest.comment

        self.assertEqual(
            test_comment._meta.get_field('text').help_text,
            'Введите текст комментария')
