from django.test import Client, TestCase
from ..forms import PostForm
from ..models import Post, User, Group
from django.urls import reverse


class PostCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user("auth")
        cls.group = Group.objects.create(
            title="Тестовая группа",
            slug="test_slug",
            description="Тестовое описание",
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text="Тестовый пост",
            group=cls.group,
        )
        cls.form = PostForm()

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_post(self):
        """Валидная форма создает запись в Post."""
        form_data = {
            "text": self.post.text * 2,
            "goup": self.group,
        }
        posts_count = Post.objects.count()
        self.authorized_client.post(
            reverse("posts:create_post"), data=form_data, follow=True
        )

        self.assertEqual(Post.objects.count(), posts_count + 1)

        # Проверяем, что создалась запись с заданным текстом
        self.assertTrue(
            Post.objects.filter(
                text=self.post.text * 2,
            ).exists()
        )

    def test_edit_post(self):
        """Валидная форма изменяет запись в Post."""
        form_data = {
            "text": self.post.text * 3,
            "goup": self.group,
        }

        # Подсчитаем количество записей в Post
        posts_count = Post.objects.count()
        # Отправляем POST-запрос
        self.authorized_client.post(
            reverse("posts:post_edit", kwargs={"post_id": self.post.id}),
            data=form_data,
            follow=True,
        )
        # # Проверяем, осталось ли число постов прежним
        self.assertEqual(Post.objects.count(), posts_count)

        # Проверяем, что создалась запись с заданным текстом
        self.assertTrue(
            Post.objects.filter(
                text=self.post.text * 3,
            ).exists()
        )
