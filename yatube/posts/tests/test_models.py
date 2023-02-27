from django.contrib.auth import get_user_model
from django.test import TestCase

from ..models import Group, Post

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user("auth")
        cls.group = Group.objects.create(
            title="группа",
            slug="slug",
            description="описание",
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text="пост",
        )

    def test_models_have_correct_object_names(self):
        """Проверяем, что у моделей корректно работает __str__."""
        group = PostModelTest.group
        group_str = group.__str__()
        self.assertEqual(group_str, group.title)

        post = PostModelTest.post
        post_str = post.__str__()
        self.assertEqual(post_str, post.text[:15] + "...")
