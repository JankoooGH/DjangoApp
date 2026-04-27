from django.db import models
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.models import User


class Task(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)

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

    def is_done_today(self):
        today = timezone.localdate()

        if self.task_type == self.TASK_ONCE:
            return self.completed

        if self.task_type == self.TASK_DAILY:
            return self.last_completed == today

        if self.task_type == self.TASK_WEEKLY:
            return self.logs.filter(date=today, completed=True).exists()

        return False

    def once_task(self):
        if self.completed:
            return
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

    def weekly_progress_count(self):
        today = timezone.localdate()
        year, week, _ = today.isocalendar()
        return self.logs.filter(
            date__week=week,
            date__year=year,
            completed=True
        ).count()

    def weekly_task(self):
        today = timezone.localdate()
        log, created = self.logs.get_or_create(
            date=today,
            defaults={"completed": True}
        )
        if not created:
            log.delete()

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

    def save(self, *args, **kwargs):
        if self.task_type == self.TASK_ONCE and not self.date:
            self.date = timezone.localdate()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.title} ({self.get_task_type_display()})"


class TaskLog(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name="logs")
    date = models.DateField(null=True, blank=True)
    completed = models.BooleanField(default=False)

    class Meta:
        unique_together = ('task', 'date')


# ============================================================
# Notatki do zadań
# ============================================================

class TaskNote(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name="notes")
    title = models.CharField(max_length=200)
    content = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"[{self.task.title}] {self.title}"


# ============================================================
# Profil użytkownika
# ============================================================

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    xp = models.IntegerField(default=0)

    def rank(self):
        if self.xp >= 2000:
            return ('👑', 'Legenda')
        elif self.xp >= 1000:
            return ('💎', 'Mistrz')
        elif self.xp >= 500:
            return ('🔥', 'Wojownik')
        elif self.xp >= 200:
            return ('⚡', 'Adept')
        else:
            return ('🌱', 'Nowicjusz')

    def xp_to_next_rank(self):
        thresholds = [200, 500, 1000, 2000]
        for t in thresholds:
            if self.xp < t:
                return t - self.xp
        return 0

    def rank_progress_percent(self):
        levels = [0, 200, 500, 1000, 2000]
        for i in range(len(levels) - 1):
            if self.xp < levels[i + 1]:
                current = self.xp - levels[i]
                total = levels[i + 1] - levels[i]
                return int((current / total) * 100)
        return 100

    def __str__(self):
        return f"{self.user.username} - {self.rank()[1]}"
