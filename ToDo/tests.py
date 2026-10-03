from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from .models import Task


class ToggleTaskSecurityTest(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='user1', password='pass12345')
        self.user2 = User.objects.create_user(username='user2', password='pass12345')
        self.task = Task.objects.create(
            user=self.user1,
            title="Cudzy nawyk",
            task_type=Task.TASK_DAILY,
        )

    def test_cannot_toggle_someone_elses_task(self):
        self.client.login(username='user2', password='pass12345')
        response = self.client.post(reverse('toggle_task', args=[self.task.id]))

        self.task.refresh_from_db()
        self.assertEqual(response.status_code, 404)
        self.assertIsNone(self.task.last_completed)


class EditTaskSecurityTest(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='user1', password='pass12345')
        self.user2 = User.objects.create_user(username='user2', password='pass12345')
        self.task = Task.objects.create(
            user=self.user1,
            title="Cudzy nawyk",
            task_type=Task.TASK_DAILY,
        )

    def test_cannot_edit_someone_elses_task(self):
        self.client.login(username='user2', password='pass12345')
        response = self.client.post(
            reverse('edit_task', args=[self.task.id]),
            {'title': 'Zhackowany tytuł', 'task_type': 'DAILY'}
        )

        self.task.refresh_from_db()
        self.assertEqual(response.status_code, 404)
        self.assertEqual(self.task.title, "Cudzy nawyk")