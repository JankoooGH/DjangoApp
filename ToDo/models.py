from django.db import models

class Task(models.Model):
    TASK_TYPES = [
        ("DAILY", "Daily"),
        ("WEEKLY", "Weekly"),
        ("ONCE", "Once"),
    ]


    title = models.CharField(max_length=100)
    completed = models.BooleanField(default=False)
    task_type = models.CharField(max_length=100, choices=TASK_TYPES, default='Once')
    last_completed = models.DateField(null=True, blank=True)
    streak = models.IntegerField(default=0)

    def count_streak(self):
        from datetime import date
        today = date.today()

        if not self.last_completed:
            if self.completed:
                self.streak = 1
                self.last_completed = today
                self.save()
            return self.streak

        if self.last_completed == today:
            return self.streak
        elif self.last_completed == today - timedelta(days=1):
            self.streak += 1
        else:
            self.streak = 1 if self.completed else 0

        if self.completed:
            self.last_completed = today

        self.save()
        return self.streak




    def __str__(self):
        return f"{self.title} ({self.get_task_type_display()})"