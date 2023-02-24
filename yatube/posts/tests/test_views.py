from django import forms
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from django.core.paginator import Page

from ..models import Group, Post

User = get_user_model()
class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Создадим запись в БД
        cls.user = User.objects.create(username='Author')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )

        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовая запись',
            group=cls.group,
        )

    def setUp(self):
        # Создаем авторизованный клиент
        self.user = User.objects.create_user(username='StasBasov')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_views_use_correct_template(self):
        POSTS_DIR = 'posts/'
        templates_pages_names = {
            reverse('posts:index'): f'{POSTS_DIR}index.html',
            reverse('posts:group',
                    kwargs={'slug': self.group.slug}): f'{POSTS_DIR}group_list.html',
            reverse('posts:post_create'): f'{POSTS_DIR}create_post.html',
            reverse('posts:profile',
                    kwargs={'username': self.user.username}): f'{POSTS_DIR}profile.html',
            reverse('posts:post_detail',
                    kwargs={'post_id': self.post.id}): f'{POSTS_DIR}post_detail.html',
        }
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

        # Проверка словаря контекста главной страницы (в нём передаётся форма)

    def test_home_page_show_correct_context(self):
        """Шаблон home_page сформирован с правильным контекстом."""
        response = (self.authorized_client.
            get(reverse('posts:index')))
        
        # Проверяем, что типы данных в словаре context соответствуют ожиданиям
        context_fields = {          
            'page_obj': Page,
        }        

        # Проверяем, что типы полей формы в словаре context соответствуют ожиданиям
        for value, expected in context_fields.items():
            with self.subTest(value=value):
                context_field = response.context.get(value)
                # Проверяет, что context_field является экземпляром
                # указанного класса
                self.assertIsInstance(context_field, expected)


    def test_task_list_page_show_correct_context(self):
        """Шаблон group_list сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:group_list'))
        # Взяли первый элемент из списка и проверили, что его содержание
        # совпадает с ожидаемым
        first_object = response.context['object_list'][0]
        task_title_0 = first_object.title
        task_text_0 = first_object.text
        task_slug_0 = first_object.slug
        self.assertEqual(task_title_0, 'Заголовок')
        self.assertEqual(task_text_0, 'Текст')
        self.assertEqual(task_slug_0, 'test-slug')

        # Проверяем, что словарь context страницы group/test-slug
        # содержит ожидаемые значения

    def test_task_detail_pages_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = (self.authorized_client.
                    get(reverse('posts:post_detail', kwargs={'slug': 'test-slug'})))
        self.assertEqual(response.context.get('task').title, 'Заголовок')
        self.assertEqual(response.context.get('task').text, 'Текст')
        self.assertEqual(response.context.get('task').slug, 'test-slug')

class PaginatorViewsTest(TestCase):
    # Здесь создаются фикстуры: клиент и 13 тестовых записей.
    ...

    def test_first_page_contains_ten_records(self):
        response = self.client.get(reverse('index'))
        # Проверка: количество постов на первой странице равно 10.
        self.assertEqual(len(response.context['group_list']), 10)

    def test_second_page_contains_three_records(self):
        # Проверка: на второй странице должно быть три поста.
        response = self.client.get(reverse('index') + '?page=2')
        self.assertEqual(len(response.context['group_list']), 3)
