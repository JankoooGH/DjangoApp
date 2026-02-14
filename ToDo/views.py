from django.shortcuts import render, redirect, get_object_or_404
from .models import Task
from .forms import TaskForm
from django.utils import timezone
from django.db.models import Q
from django.http import JsonResponse


today = timezone.localdate()

def home(request):
    form = TaskForm()

    tasks = Task.objects.filter(
        Q(task_type=Task.TASK_DAILY) |
        Q(task_type=Task.TASK_WEEKLY) |
        Q(task_type=Task.TASK_ONCE, date=today)
    )

    if request.method == "POST":
        form = TaskForm(request.POST)
        if form.is_valid():
            print("FORMULARZ POPRAWNY")
            form.save()
        else:
            print("BŁĘDY:", form.errors)

        return redirect('home')

    context = {'tasks': tasks, 'form': form}
    return render(request, 'ToDo/home.html', context)


def delete_task(request, task_id):
    task = get_object_or_404(Task, pk=task_id)
    if request.method == "POST":
        task.delete()
        return redirect('home')
    return render(request, "ToDo/confirm_delete.html", {"task": task})

def toggle_task(request, task_id):
    task = get_object_or_404(Task, pk=task_id)

    if task.task_type == Task.TASK_ONCE:
        task.once_task()
    elif task.task_type == Task.TASK_DAILY:
        task.daily_task()
    elif task.task_type == Task.TASK_WEEKLY:
        task.weekly_task()

    return redirect('home')


tasks_daily = Task.objects.filter(task_type="DAILY")
tasks_weekly = Task.objects.filter(task_type="WEEKLY")
tasks_once = Task.objects.filter(task_type="ONCE")

context = {
    "tasks_daily": tasks_daily,
    "tasks_weekly": tasks_weekly,
    "tasks_once": tasks_once,
}

# kalendarz

def calendar_view(request):
    return render(request, "kalendarz/calendar.html")

def calendar_events(request):
    events = []

    tasks = Task.objects.filter(task_type=Task.TASK_ONCE)

    for task in tasks:
        if task.date:
            events.append({
                "title": task.title,
                "start": task.date.isoformat(),
            })

    return JsonResponse(events, safe=False)