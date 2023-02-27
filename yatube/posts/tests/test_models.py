from django.contrib.auth import get_user_model
from django.test import TestCase

from ..models import Group, Post

User = get_user_model()


class PostModelTest(TestCase):
    def test_models_have_correct_object_names(self):
        """У моделей корректно работает __str__."""

        user = User.objects.create_user("auth")
        group = Group.objects.create(slug="slug")
        post = Post.objects.create(author=user)

        self.assertEqual(group.__str__(), group.title)
        self.assertEqual(post.__str__(), post.text[:15] + "...")
