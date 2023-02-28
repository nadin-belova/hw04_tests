from django.contrib.auth import get_user_model
from django.test import TestCase

from ..models import Post

User = get_user_model()


class PostModelTest(TestCase):
    def test_models_have_correct_object_names(self):
        """
        У моделей метод __str__ выводит первые 15 символов.
        """

        user = User.objects.create_user("auth")

        short_post = Post.objects.create(
            author=user,
            text='Короткий пост',
        )
        self.assertEqual(str(short_post), 'Короткий пост...')

        long_post = Post.objects.create(
            author=user,
            text='Не более 15 символов может уместиться в превью',
        )
        self.assertEqual(str(long_post), "Не более 15 сим...")
