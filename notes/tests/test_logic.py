"""Модуль тестирования логики приложения news."""

# news/tests/test_logic.py
from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()

success_url = reverse('notes:success')


class TestNoteCreation(TestCase):
    """Тестирует логику создания заметки."""

    TITLE = 'Заметка 100500'
    TEXT = 'Текст 100500'
    SLUG = 'zametka-100500'

    @classmethod
    def setUpTestData(cls):
        """Создай данные для теста."""
        cls.user = User.objects.create(username='Автор Заметок')
        cls.auth_client = Client()
        cls.auth_client.force_login(cls.user)
        cls.form_data = {
            'title': cls.TITLE,
            'text': cls.TEXT,
            'slug': cls.SLUG
        }
        cls.url = reverse('notes:add')

    def test_anonymous_user_cant_create_note(self):
        """Проверь невозможность для анонима создать заметку."""
        self.client.post(self.url, data=self.form_data)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 0)

    def test_user_can_create_note(self):
        """Проверь возможность пользователя создать заметку."""
        response = self.auth_client.post(self.url, data=self.form_data)
        self.assertRedirects(response, success_url)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)
        note = Note.objects.get()
        self.assertEqual(note.title, self.TITLE)
        self.assertEqual(note.text, self.TEXT)
        self.assertEqual(note.slug, self.SLUG)

    def test_slug_generator(self):
        """Проверь работу генератора slug-записей."""
        self.auth_client.post(self.url, data={
            'title': self.TITLE,
            'text': self.TEXT,
            }
        )
        note = Note.objects.get()
        self.assertEqual(note.slug, self.SLUG)


class TestNoteEditDelete(TestCase):
    """Тестирует логику редактирования/удаления заметки."""

    TITLE = 'Заметка 100500'
    NEW_TITLE = 'Заметка 1005001'
    TEXT = 'Текст 100500'
    NEW_TEXT = 'Текст 2 100500'
    SLUG = 'zametka-100500'

    @classmethod
    def setUpTestData(cls):
        """Создай данные для теста."""
        cls.author = User.objects.create(username='Автор заметки')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.reader = User.objects.create(username='Другой пользователь')
        cls.reader_client = Client()
        cls.reader_client.force_login(cls.reader)
        cls.note = Note.objects.create(
            title=cls.TITLE,
            text=cls.TEXT,
            slug=cls.SLUG,
            author=cls.author,
        )
        cls.note_url = reverse('notes:detail', args=(cls.note.slug,))
        cls.edit_url = reverse('notes:edit', args=(cls.note.slug,))
        cls.delete_url = reverse('notes:delete', args=(cls.note.slug,))
        cls.form_data = {'title': cls.NEW_TITLE, 'text': cls.NEW_TEXT}

    def test_author_can_delete_note(self):
        """Проверь возможность автора удалить заметку."""
        response = self.author_client.delete(self.delete_url)
        self.assertRedirects(response, success_url)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 0)

    def test_reader_can_t_delete_note(self):
        """Проверь невозможность пользователя удалить чужую заметку."""
        response = self.reader_client.delete(self.delete_url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)

    def test_author_can_edit_note(self):
        """Проверь возможность автора править заметку."""
        response = self.author_client.post(self.edit_url, data=self.form_data)
        self.assertRedirects(response, success_url)
        self.note.refresh_from_db()
        self.assertEqual(self.note.title, self.NEW_TITLE)
        self.assertEqual(self.note.text, self.NEW_TEXT)

    def test_reader_can_t_edit_note(self):
        """Проверь невозможность пользователя править чужую заметку."""
        response = self.reader_client.post(self.edit_url, data=self.form_data)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.note.refresh_from_db()
        self.assertEqual(self.note.title, self.TITLE)
        self.assertEqual(self.note.text, self.TEXT)
