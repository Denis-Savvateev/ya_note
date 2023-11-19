"""Модуль тестирования контента."""

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()
COUNT = 3


class TestDetailPage(TestCase):
    """Тестирует контент, страницы новости."""

    @classmethod
    def setUpTestData(cls):
        """Создай данные для теста."""
        cls.author = User.objects.create(username='Автор')
        cls.reader = User.objects.create(username='Читатель')
        Note.objects.bulk_create(
            Note(
                title=f'Заметка {index}',
                text=f'Текст заметки {index}',
                slug=f'zametka-{index}',
                author=cls.author,
            )
            for index in range(1, COUNT+1)
        )

    def test_notes_list(self):
        """Проверь количество записей в Списке заметок."""
        self.client.force_login(self.author)
        response = self.client.get(reverse('notes:list'))
        object_list = response.context['object_list']
        notes_count = len(object_list)
        self.assertEqual(notes_count, COUNT)
