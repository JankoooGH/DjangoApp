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
    task_type = models.CharField(
        max_length=10,
        choices=TASK_TYPES,
        default=TASK_ONCE
    )

    # ONCE
    date = models.DateField(null=True, blank=True)
    completed = models.BooleanField(default=False)

    # DAILY
    last_completed = models.DateField(null=True, blank=True)
    streak = models.IntegerField(default=0)

    # WEEKLY
    weekly_target = models.IntegerField(null=True, blank=True)

    # --------------------------------------------------
    # COMMON HELPERS
    # --------------------------------------------------

    def is_done_today(self):
        today = timezone.localdate()

        if self.task_type == self.TASK_ONCE:
            return self.completed

        if self.task_type == self.TASK_DAILY:
            return self.last_completed == today

        if self.task_type == self.TASK_WEEKLY:
            return self.logs.filter(date=today, completed=True).exists()

        return False

    # --------------------------------------------------
    # ONCE
    # --------------------------------------------------

    def complete_once(self):
        if not self.completed:
            self.completed = True
            self.save()

    # --------------------------------------------------
    # DAILY
    # --------------------------------------------------

    def complete_daily(self):
        today = timezone.localdate()

        if self.last_completed == today:
            return

        if self.last_completed == today - timedelta(days=1):
            self.streak += 1
        else:
            self.streak = 1

        self.last_completed = today
        self.save()

    # --------------------------------------------------
    # WEEKLY
    # --------------------------------------------------

    def toggle_weekly(self):
        today = timezone.localdate()

        log, created = self.logs.get_or_create(
            date=today,
            defaults={"completed": True}
        )

        if not created:
            log.completed = not log.completed
            log.save()

    def weekly_progress(self):
        if not self.weekly_target:
            return 0

        today = timezone.localdate()
        week_start = today - timedelta(days=today.weekday())
        week_end = week_start + timedelta(days=6)

        return (
            self.logs
            .filter(date__range=(week_start, week_end), completed=True)
            .values("date")
            .distinct()
            .count()
        )

    @property
    def weekly_streak(self):
        if self.task_type != self.TASK_WEEKLY or not self.weekly_target:
            return 0

        today = timezone.localdate()
        week_start = today - timedelta(days=today.weekday())

        streak = 0

        while True:
            week_end = week_start + timedelta(days=6)

            completed_days = (
                self.logs
                .filter(date__range=(week_start, week_end), completed=True)
                .values("date")
                .distinct()
                .count()
            )

            if completed_days >= self.weekly_target:
                streak += 1
                week_start -= timedelta(days=7)
            else:
                break

        return streak

    # --------------------------------------------------

    def save(self, *args, **kwargs):
        if self.task_type == self.TASK_ONCE and not self.date:
            self.date = timezone.localdate()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.title} ({self.get_task_type_display()})"


class TaskLog(models.Model):
    task = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        related_name="logs"
    )
    date = models.DateField()
    completed = models.BooleanField(default=False)

    class Meta:
        unique_together = ("task", "date")

    def __str__(self):
        return f"{self.task.title} - {self.date} - {self.completed}"
