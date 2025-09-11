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



    def __str__(self):
        return f"{self.title} ({self.get_task_type_display()})"