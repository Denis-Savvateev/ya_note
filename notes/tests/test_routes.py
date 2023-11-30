"""Модуль тестирования путей приложения notes."""

from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.urls import reverse

from notes.tests.const import (
    NoteTest,
    LOGIN_URL,
)

User = get_user_model()


class TestRoutes(NoteTest):
    """Тестируем пути приложения notes."""

    def test_pages_availability_for_all(self):
        """Проверь доступность страниц анониму."""
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

    def test_pages_availability_user(self):
        """Проверь доступность страниц пользователю."""
        urls = (
            'notes:add',
            'notes:list',
            'notes:success',
            'users:login',
            'users:logout',
            'users:signup',
        )
        for name in urls:
            with self.subTest(name=name):
                url = reverse(name)
                response = self.reader_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_availability_for_notes(self):
        """Проверь доступность страниц заметки только автору."""
        clients_statuses = (
            (self.author_client, HTTPStatus.OK),
            (self.reader_client, HTTPStatus.NOT_FOUND),
            (self.client, HTTPStatus.FOUND),
        )
        note_slug = self.note.slug
        for user_client, status in clients_statuses:
            for name, slug in (
                ('notes:edit', note_slug),
                ('notes:detail', note_slug),
                ('notes:delete', note_slug),
            ):
                with self.subTest(user_client=user_client, name=name):
                    url = reverse(name, kwargs={'slug': slug})
                    response = user_client.get(url)
                    self.assertEqual(response.status_code, status)

    def test_redirect_for_anonymous_client(self):
        """Проверь перенаправление анонимного пользователя."""
        for name, kwargs in (
            ('notes:edit', {'slug': self.note.slug}),
            ('notes:detail', {'slug': self.note.slug}),
            ('notes:delete', {'slug': self.note.slug}),
            ('notes:add', {}),
            ('notes:list', {}),
            ('notes:success', {}),

        ):
            with self.subTest(name=name):
                url = reverse(name, kwargs=kwargs)
                redirect_url = f'{LOGIN_URL}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)
