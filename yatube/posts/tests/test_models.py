from django.test import TestCase

from ..models import Group, Post, User


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='testslug',
            description='Для тестов',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тест, тест, тест',
        )

    def test_models_have_correct_object_names(self):
        """Проверяем, что у моделей корректно работает __str__."""
        test_post = str(PostModelTest.post)
        test_post_str = PostModelTest.post.text[:15]
        self.assertEqual(test_post, test_post_str,
                         'Не корректно работает __str__ у модели post')

        test_group = str(PostModelTest.group)
        test_group_str = PostModelTest.group.title
        self.assertEqual(test_group, test_group_str,
                         'Не корректно работает __str__ у модели group')

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
