from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Group, Post

User = get_user_model()
class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Создадим запись в БД
        Post.objects.create(

            text='Текст',
            slug='test-slug',
        )

    def setUp(self):
        # Создаем авторизованный клиент
        self.user = User.objects.create_user(username='StasBasov')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_views_use_correct_template(self):
        templates_pages_names = {
            reverse('posts:index'): 'index.html',
            reverse('posts:group_slug',
                    kwargs={'slug': self.group.slug}): 'group.html',
            reverse('posts:new_post'): 'new_post.html',
            reverse('posts:profile',
                    kwargs={'username': self.user.username}): 'profile.html',
            reverse('posts:post',
                    kwargs={'username': self.user.username,
                            'post_id': self.post.id}): 'post.html',
            reverse('posts:follow_index'): 'follow.html',
        }
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

        # Проверка словаря контекста главной страницы (в нём передаётся форма)

    def test_home_page_show_correct_context(self):
        """Шаблон home сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('deals:index'))
        # Словарь ожидаемых типов полей формы:
        # указываем, объектами какого класса должны быть поля формы
        form_fields = {
            'title': forms.fields.CharField,
            # При создании формы поля модели типа TextField
            # преобразуются в CharField с виджетом forms.Textarea
            'text': forms.fields.CharField,
            'slug': forms.fields.SlugField,
        }

        # Проверяем, что типы полей формы в словаре context соответствуют ожиданиям
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                # Проверяет, что поле формы является экземпляром
                # указанного класса
                self.assertIsInstance(form_field, expected)



    def test_task_list_page_show_correct_context(self):
        """Шаблон group_list сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('deals:group_list'))
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
                    get(reverse('deals:post_detail', kwargs={'slug': 'test-slug'})))
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