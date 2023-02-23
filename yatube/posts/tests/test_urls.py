
from django.contrib.auth import get_user_model
from django.test import TestCase, Client

from ..models import Group, Post

User = get_user_model()

class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='NoName')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание'
        )
        cls.post = Post.objects.create(
            text="Текст тестового поста",
            author=cls.user
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_posts_urls_uses_correct_template(self):
        urls = {
            '/': 'posts/index.html',
            '/group/test-slug/': 'posts/group_list.html',
            '/profile/NoName/': 'posts/profile.html',
            '/posts/1/': 'posts/post_detail.html',
            '/create/': 'posts/create_post.html',
            '/posts/1/edit/': 'posts/create_post.html',
        }
        for address, template in urls.items():
            with self.subTest(template=template):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)

    # def test_404_page_uses_custom_template(self):
    #     template = 'core/404.html'
    #     url = '/unexsisting_page/'
    #     response = self.guest_client.get(url)
    #     self.assertTemplateUsed(response, template)
    #

    class MyTestCase(TestCase):
        #запрос к несуществующей странице вернёт ошибку 404.
        def test_page_not_found(self):
            url = '/unexsisting_page/'
            response = self.client.get(url)
            self.assertEqual(response.status_code, 404)
