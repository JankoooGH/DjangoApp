from django.db import models
from django.utils import timezone
from datetime import timedelta

class Task(models.Model):
    TASK_DAILY = "DAILY"
    TASK_WEEKLY = "WEEKLY"
    TASK_ONCE = "ONCE"
    TASK_TYPES = [
        (TASK_DAILY, "Daily"),
        (TASK_WEEKLY, "Weekly"),
        (TASK_ONCE, "Once"),
    ]

    title = models.CharField(max_length=200)
    task_type = models.CharField(max_length=10, choices=TASK_TYPES, default=TASK_ONCE)

    # ONCE
    date = models.DateField(null=True, blank=True)
    completed = models.BooleanField(default=False)

    # DAILY
    last_completed = models.DateField(null=True, blank=True)
    streak = models.IntegerField(default=0)

    # WEEKLY
    weekly_target = models.IntegerField(null=True, blank=True)
    weekly_progress = models.IntegerField(default=0)
    last_week = models.CharField(max_length=10, null=True, blank=True)

    def is_complete_today(self):
        today = timezone.localdate()
        return self.last_completed == today

    def once_task(self):
        self.completed = True
        self.save()

    def daily_task(self):
        today = timezone.localdate()
        if self.last_completed == today:
            return
        elif self.last_completed == today - timedelta(days=1):
            self.streak += 1
        else:
            self.streak = 1
        self.last_completed = today
        self.save()

    def weekly_task(self):
        today = timezone.localdate()
        year, week, _ = today.isocalendar()
        current_week = f"{year}-{week}"
        target = self.weekly_target or 1

        if self.last_week != current_week:
            if self.weekly_progress >= target:
                self.streak += 1
            else:
                self.streak = 0
            self.weekly_progress = 0
            self.last_week = current_week

        if self.weekly_progress < target:
            self.weekly_progress += 1
            if self.weekly_progress == target:
                self.streak += 1

        self.save()

    def __str__(self):
        return f"{self.title} ({self.get_task_type_display()})"