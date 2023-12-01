"""Модуль тестирования путей приложения notes."""

from http import HTTPStatus

from django.contrib.auth import get_user_model

from notes.tests.const import (
    NoteTest,
    HOME_URL,
    LOGIN_URL,
    LOGOUT_URL,
    SIGNUP_URL,
    ADD_URL,
    LIST_URL,
    SUCCESS_URL,
)

User = get_user_model()


class TestRoutes(NoteTest):
    """Тестируем пути приложения notes."""

    def test_pages_availability_for_all(self):
        """Проверь доступность страниц анониму."""
        urls = (
            HOME_URL,
            LOGIN_URL,
            LOGOUT_URL,
            SIGNUP_URL,
        )
        for url in urls:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_pages_availability_user(self):
        """Проверь доступность страниц пользователю."""
        urls = (
            ADD_URL,
            LIST_URL,
            SUCCESS_URL,
            LOGIN_URL,
            LOGOUT_URL,
            SIGNUP_URL,
        )
        for url in urls:
            with self.subTest(url=url):
                response = self.reader_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_availability_for_notes(self):
        """Проверь доступность страниц заметки только автору."""
        clients_statuses = (
            (self.author_client, HTTPStatus.OK),
            (self.reader_client, HTTPStatus.NOT_FOUND),
            (self.client, HTTPStatus.FOUND),
        )
        for user_client, status in clients_statuses:
            for url in (
                self.edit_url,
                self.note_url,
                self.delete_url,
            ):
                with self.subTest(user_client=user_client, url=url):
                    response = user_client.get(url)
                    self.assertEqual(response.status_code, status)

    def test_redirect_for_anonymous_client(self):
        """Проверь перенаправление анонимного пользователя."""
        for url in (
            self.edit_url,
            self.note_url,
            self.delete_url,
            ADD_URL,
            LIST_URL,
            SUCCESS_URL,

        ):
            with self.subTest(url=url):
                redirect_url = f'{LOGIN_URL}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)
