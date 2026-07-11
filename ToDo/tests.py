from django.test import TestCase
from django.contrib.auth.models import User
from .models import Task

class ToggleTaskSecurityTest(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user('user1', password='pass123')
        self.user2 = User.objects.create_user('user2', password='pass123')
        self.task = Task.objects.create(
            user=self.user1, title='Cudze zadanie', task_type=Task.TASK_ONCE
        )

    def test_user_cannot_toggle_foreign_task(self):
        self.client.login(username='user2', password='pass123')
        response = self.client.post(f'/toggle/{self.task.id}/')
        self.task.refresh_from_db()
        self.assertEqual(response.status_code, 404)
        self.assertFalse(self.task.completed)