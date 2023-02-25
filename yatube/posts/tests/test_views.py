from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from ..forms import PostForm

from ..models import Group, Post

User = get_user_model()


class PostPageTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
            group=cls.group,
        )

    def setUp(self):
        # Создаем авторизованный клиент
        self.authorized_client = Client()
        # Авторизуем пользователя
        self.authorized_client.force_login(PostPageTests.user)

    # Проверяем используемые шаблоны
    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        # Собираем в словарь пары "имя_html_шаблона: reverse(name)"
        templates_pages_names = [
            ('posts/index.html', reverse('posts:index')),
            (
                'posts/group_list.html',
                reverse('posts:group_list',
                        kwargs={'slug': self.group.slug})
            ),
            (
                'posts/profile.html',
                reverse('posts:profile',
                        kwargs={'username': self.user.get_username()})
            ),
            (
                'posts/post_detail.html',
                reverse('posts:post_detail',
                        kwargs={'post_id': self.post.id})
            ),
            ('posts/create_post.html', reverse
             ('posts:post_edit', kwargs={'post_id': self.post.id})),
            ('posts/create_post.html', reverse('posts:create_post')),
        ]
        # Проверяем, что при обращении к name вызывается
        # соответствующий HTML-шаблон
        for template, reverse_name in templates_pages_names:
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    # Проверяем, что словарь context страницы /index
    # в первом элементе списка page_obj содержит ожидаемые значения
    def test_index_page_correct_context(self):
        """Шаблон index.html сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:index'))
        # Взяли первый элемент из списка и проверили, что его содержание
        # совпадает с ожидаемым
        first_object = response.context['page_obj'][0]

        self.assertEqual(first_object.group.title, PostPageTests.group.title)
        self.assertEqual(first_object.group.slug, PostPageTests.group.slug)
        self.assertEqual(
            first_object.group.description,
            PostPageTests.group.description)

        self.assertEqual(
            first_object.author.username,
            PostPageTests.post.author.get_username())
        self.assertEqual(first_object.text, PostPageTests.post.text)

    # Проверяем, что словарь context страницы /group_list
    # содержит список постов отфильтрованных по группе
    def test_group_list_page_correct_context(self):
        """Шаблон group_list.html сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:group_list', kwargs={'slug': self.group.slug}))
        first_object = response.context['page_obj'][0]

        self.assertEqual(first_object.group.title, self.group.title)
        self.assertEqual(first_object.group.slug, self.group.slug)
        self.assertEqual(first_object.
                         group.description, self.group.description)

        self.assertEqual(first_object.
                         author.username, self.post.author.get_username())
        self.assertEqual(first_object.text, self.post.text)

        self.group_2 = Group.objects.create(
            title='Тестовая группа 2',
            slug='test_slug_2',
            description='Тестовое описание группы 2',
        )

        self.post_2 = Post.objects.create(
            author=self.user,
            text='Тестовый пост 2',
            group=self.group_2,
        )

        response = self.authorized_client.get
        (reverse('posts:group_list', kwargs={'slug': self.group_2.slug}))
        self.assertEqual(
            response.context['page_obj'][0].text, self.post_2.text)

        self.post_2.delete()
        self.group_2.delete()

    # Проверяем, что словарь context страницы /profile
    # содержит список постов отфильтрованных по пользователю
    def test_profile_page_correct_context(self):
        """Шаблон profile.html сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse(
                'posts:profile',
                kwargs={'username': self.user.get_username()}
            )
        )
        first_object = response.context['page_obj'][0]

        self.assertEqual(first_object.group.title, self.group.title)
        self.assertEqual(first_object.group.slug, self.group.slug)
        self.assertEqual(first_object.
                         group.description, self.group.description)
        self.assertEqual(
            first_object.author.username,
            self.post.author.get_username())
        self.assertEqual(first_object.text, self.post.text)

        self.user_2 = User.objects.create_user(username='user_2')

        self.post_2 = Post.objects.create(
            author=self.user_2,
            text='Тестовый пост 2',
        )

        response = self.authorized_client.get(
            reverse('posts:profile',
                    kwargs={'username': self.user_2.get_username()}))
        self.assertEqual(response.context
                         ['page_obj'][0].text, self.post_2.text)

        self.post_2.delete()
        self.user_2.delete()

    # Проверяем, что словарь context страницы /post_detail
    # содержит список постов отфильтрованных по id
    def test_post_detail_page_correct_context(self):
        """Шаблон post_detail.html сформирован с правильным контекстом."""
        response = self.authorized_client.get
        (reverse('posts:post_detail', kwargs={'post_id': self.post.id}))
        post = response.context['post']

        self.assertEqual(post.group.title, self.group.title)
        self.assertEqual(post.group.slug, self.group.slug)
        self.assertEqual(post.group.description, self.group.description)

        self.assertEqual(post.author.username, self.post.author.get_username())
        self.assertEqual(post.text, self.post.text)

        count = response.context['post_count']
        self.assertEqual(count, 1)

    # Проверяем, что словарь context страницы /create_post
    # содержит форму редактирования поста отфильтрованного по id
    def test_edit_post_page_correct_context(self):
        """Шаблон create_post.html сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:post_edit', kwargs={'post_id': self.post.id}))

        form = response.context['form']
        self.assertIsInstance(form, PostForm)

        is_edit = response.context['is_edit']
        self.assertEqual(is_edit, True)
        post_id = response.context['post_id']
        self.assertEqual(post_id, 1)

    # Проверяем, что словарь context страницы /create_post
    # содержит форму создания поста
    def test_create_post_page_correct_context(self):
        """Шаблон create_post.html сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:create_post'))
        form = response.context['form']
        self.assertIsInstance(form, PostForm)


class PaginatorViewsTest(TestCase):
    ALL_POSTS_COUNT = 12
    FIRST_PAGE_POSTS_COUNT = 10
    SECOND_PAGE_POSTS_COUNT = ALL_POSTS_COUNT - FIRST_PAGE_POSTS_COUNT
    PAGE_ID = 2

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug',
            description='Тестовое описание',
        )
        cls.posts = []
        for _ in range(cls.ALL_POSTS_COUNT):
            post = Post.objects.create(
                author=cls.user,
                text='Тестовый пост',
                group=cls.group,
            )
            cls.posts.append(post)

    def setUp(self):
        # Создаем авторизованный клиент
        self.authorized_client = Client()
        # Авторизуем пользователя
        self.authorized_client.force_login(self.user)

    def __test_paginator(self, reverse_name: str, kwargs=None):
        response = self.client.get(
            reverse(reverse_name, kwargs=kwargs) + f'?page={self.PAGE_ID}')
        self.assertEqual(len(
            response.context['page_obj']), self.SECOND_PAGE_POSTS_COUNT)

        response = self.client.get(reverse(reverse_name, kwargs=kwargs))
        self.assertEqual(len(response.context['page_obj']),
                         self.FIRST_PAGE_POSTS_COUNT)

    def test_index_paginator(self):
        self.__test_paginator('posts:index')

    def test_group_list_paginator(self):
        self.__test_paginator(
            'posts:group_list',
            kwargs={'slug': self.group.slug}
        )

    def test_profile_paginator(self):
        self.__test_paginator(
            'posts:profile',
            kwargs={'username': self.user.get_username()}
        )
