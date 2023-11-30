"""Модуль тестирования логики приложения news."""

from http import HTTPStatus

from pytils.translit import slugify

from notes.forms import WARNING
from notes.models import Note
from notes.tests.const import (
    NoteTest,
    TITLE,
    TEXT,
    SLUG,
    NEW_TITLE,
    NEW_TEXT,
    NEW_FORM_DATA,
    ADD_URL,
    SUCCESS_URL,
)


class TestNoteCreation(NoteTest):
    """Тестирует логику создания заметки."""

    def test_anonymous_user_cant_create_note(self):
        """Проверь невозможность для анонима создать заметку."""
        notes_count_before = Note.objects.count()
        self.client.post(ADD_URL, data=NEW_FORM_DATA)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, notes_count_before)

    def test_user_can_create_note(self):
        """Проверь возможность пользователя создать заметку."""
        notes_before = Note.objects.all()
        response = self.author_client.post(ADD_URL, data=NEW_FORM_DATA)
        self.assertRedirects(response, SUCCESS_URL)
        notes = Note.objects.all()
        self.assertNotEqual(notes, notes_before)

    def test_slug_generator(self):
        """Проверь работу генератора slug-записей."""
        Note.objects.all().delete()
        self.author_client.post(ADD_URL, data=NEW_FORM_DATA)
        note = Note.objects.get()
        expected_slug = slugify(NEW_FORM_DATA['title'])
        self.assertEqual(note.slug, expected_slug)

    def test_not_unique_slug(self):
        """Проверь контроль уникальности slug-записи."""
        new_form_data = {
            'title': NEW_TITLE,
            'text': NEW_TEXT,
            'slug': SLUG,
        }
        response = self.author_client.post(ADD_URL, data=new_form_data)
        self.assertFormError(response, 'form', 'slug',
                             errors=(SLUG + WARNING))


class TestNoteEditDelete(NoteTest):
    """Тестирует логику редактирования/удаления заметки."""

    def test_author_can_delete_note(self):
        """Проверь возможность автора удалить заметку."""
        response = self.author_client.delete(self.delete_url)
        self.assertRedirects(response, SUCCESS_URL)
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
        response = self.author_client.post(self.edit_url,
                                           data=NEW_FORM_DATA)
        self.assertRedirects(response, SUCCESS_URL)
        self.note.refresh_from_db()
        self.assertEqual(self.note.title, NEW_TITLE)
        self.assertEqual(self.note.text, NEW_TEXT)

    def test_reader_can_t_edit_note(self):
        """Проверь невозможность пользователя править чужую заметку."""
        response = self.reader_client.post(self.edit_url,
                                           data=NEW_FORM_DATA)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.note.refresh_from_db()
        self.assertEqual(self.note.title, TITLE)
        self.assertEqual(self.note.text, TEXT)
