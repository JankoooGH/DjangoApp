from django.shortcuts import render, redirect, get_object_or_404
from .models import Task
from django.utils import timezone
from django.db.models import Q
from django.http import JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .forms import TaskForm, RegisterForm


def auth_view(request):
    """Strona logowania i rejestracji (auth.html)"""
    if request.user.is_authenticated:
        return redirect('home')

    login_form = None
    register_form = RegisterForm()
    active_tab = 'login'
    error = None

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'login':
            active_tab = 'login'
            username = request.POST.get('username')
            password = request.POST.get('password')
            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
                return redirect('home')
            else:
                error = 'Nieprawidłowy login lub hasło.'

        elif action == 'register':
            active_tab = 'register'
            register_form = RegisterForm(request.POST)
            if register_form.is_valid():
                user = register_form.save()
                login(request, user)
                return redirect('home')

    return render(request, 'ToDo/auth.html', {
        'register_form': register_form,
        'active_tab': active_tab,
        'error': error,
    })


def logout_view(request):
    logout(request)
    return redirect('auth')


@login_required(login_url='auth')
def home(request):
    today = timezone.localdate()
    form = TaskForm()

    tasks = Task.objects.filter(
        user=request.user  # ← dodaj to
    ).filter(
        Q(task_type=Task.TASK_DAILY) |
        Q(task_type=Task.TASK_WEEKLY) |
        Q(task_type=Task.TASK_ONCE, date=today)
    )

    if request.method == "POST":
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.user = request.user  # ← przypisz użytkownika
            task.save()
        return redirect('home')

    context = {'tasks': tasks, 'form': form}
    return render(request, 'ToDo/main.html', context)

def landing(request):
    if request.user.is_authenticated:
        return redirect('home')
    return render(request, 'ToDo/home.html')

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


# kalendarz

def calendar_view(request):
    return render(request, "kalendarz/calendar.html")

def calendar_events(request):
    events = []
    tasks = Task.objects.filter(task_type=Task.TASK_ONCE, user=request.user)

    for task in tasks:
        if task.date:
            events.append({
                "title": task.title,
                "start": task.date.isoformat(),
            })

    return JsonResponse(events, safe=False)