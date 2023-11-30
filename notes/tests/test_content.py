"""Модуль тестирования контента."""

from django import forms
# from django.contrib.auth import get_user_model
from django.urls import reverse

from notes.models import Note
from notes.tests.const import NoteTest

# User = get_user_model()


class TestDetailPage(NoteTest):
    """Тестирует контент, страницы новости."""

    def test_notes_list_for_different_users(self):
        """Проверь наличие заметки в списке context только автора."""
        cases = ((self.author_client, True), (self.reader_client, False))
        note = Note.objects.get()
        for client, note_in_list in cases:
            with self.subTest(client=client):
                response = client.get(reverse('notes:list'))
                self.assertIn('object_list',
                              response.context,
                              msg='object_list not in context')
                object_list = response.context['object_list']
                self.assertEqual((note in object_list), note_in_list)

    def test_pages_contains_form(self):
        """Проверь наличие формы на страницах создания и редактирования."""
        cases = (
            ('notes:add', None),
            ('notes:edit', (Note.objects.get().slug,))
        )
        for name, args in cases:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                response = self.author_client.get(url)
                self.assertIn('form', response.context)
                self.assertIsInstance(response.context['form'],
                                      forms.ModelForm)
