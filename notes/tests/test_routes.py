"""Модуль тестирования путей приложения notes."""

from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class TestRoutes(TestCase):
    """Тестируем пути приложения notes."""

    @classmethod
    def setUpTestData(cls):
        """Создай данные для теста."""
        cls.author = User.objects.create(username='Лев Толстой')
        cls.reader = User.objects.create(username='Читатель простой')
        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст заметки',
            slug='zagolovok',
            author=cls.author,
        )

    def test_pages_availability(self):
        """Проверь доступность страниц из списка."""
        urls = (
            'notes:home',
            'users:login',
            'users:logout',
            'users:signup',
        )
        for name in urls:
            with self.subTest(name=name):
                # Передаём имя и позиционный аргумент в reverse()
                # и получаем адрес страницы для GET-запроса:
                url = reverse(name)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_availability_for_notes(self):
        """Проверь доступность страниц заметки только автору."""
        users_statuses = (
            (self.author, HTTPStatus.OK),
            (self.reader, HTTPStatus.NOT_FOUND),
        )
        note_slug = self.note.slug
        for user, status in users_statuses:
            self.client.force_login(user)
            for name, slug in (
                ('notes:edit', note_slug),
                ('notes:detail', note_slug),
                ('notes:delete', note_slug),
            ):
                with self.subTest(user=user, name=name):
                    url = reverse(name, kwargs={'slug': slug})
                    response = self.client.get(url)
                    self.assertEqual(response.status_code, status)

    def test_redirect_for_anonymous_client(self):
        """Проверь перенаправление анонимного пользователя."""
        login_url = reverse('users:login')
        for name in (
            'notes:edit',
            'notes:detail',
            'notes:delete',
        ):
            with self.subTest(name=name):
                url = reverse(name, kwargs={'slug': self.note.slug})
                redirect_url = f'{login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)
        for name in (
            'notes:add',
            'notes:list',
            'notes:success',
        ):
            with self.subTest(name=name):
                url = reverse(name,)
                redirect_url = f'{login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)
