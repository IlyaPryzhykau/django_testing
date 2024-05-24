from http import HTTPStatus

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from notes.models import Note


User = get_user_model()


class TestRoutes(TestCase):
    """Тесты для проверки доступности страниц и маршрутов."""
    @classmethod
    def setUpTestData(cls):
        """Создание тестовых данных для всех тестов в классе."""
        cls.author = User.objects.create(username='Лев Толстой')
        cls.note_author = Note.objects.create(
            title='Заголовок',
            text='Текст заметки',
            slug='Zagolovok',
            author=cls.author
        )
        cls.routes_names = (
            ('notes:add', None),
            ('notes:list', None),
            ('notes:success', None),
            ('notes:edit', (cls.note_author.slug,)),
            ('notes:detail', (cls.note_author.slug,)),
            ('notes:delete', (cls.note_author.slug,)),
        )

    def test_pages_availability(self):
        """Тест: Проверка доступности общедоступных страниц."""
        urls = (
            'notes:home',
            'users:login',
            'users:logout',
            'users:signup',
        )

        for name in urls:
            with self.subTest(name=name):
                url = reverse(name)
                response = self.client.get(url)

                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_availability_pages_for_user(self):
        """Тест: Проверка доступности страниц для автора."""
        self.client.force_login(self.author)
        for name, args in self.routes_names:
            with self.subTest(name=name, args=args):
                url = reverse(name, args=args)
                response = self.client.get(url)

                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_availability_for_anonymous_pages_add_list_success(self):
        """
        Тест: Проверка недоступности страниц для
        анонимного пользователя.
        """
        self.client.logout()
        for name, args in self.routes_names:
            with self.subTest(name=name, args=args):
                url = reverse(name, args=args)
                response = self.client.get(url)

            self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_redirect_for_anonymous_user(self):
        """
        Тест: Проверка перенаправления анонимного пользователя
        на страницу регистрации.
        """
        login_url = reverse('users:login')

        for name, args in self.routes_names:
            with self.subTest(name=name, args=args):
                url = reverse(name, args=args)
                response = self.client.get(url)
                expected_url = f"{login_url}?next={url}"

                self.assertRedirects(response, expected_url)
