"""Модуль констант и абстрактных классов."""

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.models import Note

TITLE = 'Заметка 100500'
TEXT = 'Текст 100500'
SLUG = 'zametka-100500'
NEW_TITLE = 'Заметка 1005001'
NEW_TEXT = 'Текст 2 1005001'
HOME_URL = reverse('notes:home')
ADD_URL = reverse('notes:add')
SUCCESS_URL = reverse('notes:success')
LIST_URL = reverse('notes:list')
LOGIN_URL = reverse('users:login')
LOGOUT_URL = reverse('users:logout')
SIGNUP_URL = reverse('users:signup')
USER = get_user_model()
FORM_DATA = {
    'title': TITLE,
    'text': TEXT,
    'slug': SLUG
}
NEW_FORM_DATA = {
    'title': NEW_TITLE,
    'text': NEW_TEXT,
}


class NoteTest(TestCase):
    """Абстрактный класс для тестов."""

    @classmethod
    def setUpTestData(cls):
        """Создай данные для теста."""
        cls.author = USER.objects.create(username='Автор')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.reader = USER.objects.create(username='Читатель')
        cls.reader_client = Client()
        cls.reader_client.force_login(cls.reader)
        cls.note = Note.objects.create(
            title=TITLE,
            text=TEXT,
            slug=SLUG,
            author=cls.author,
        )
        cls.note_url = reverse('notes:detail', args=(cls.note.slug,))
        cls.edit_url = reverse('notes:edit', args=(cls.note.slug,))
        cls.delete_url = reverse('notes:delete', args=(cls.note.slug,))
