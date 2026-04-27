from django.shortcuts import render, redirect, get_object_or_404
from .models import Task, UserProfile, TaskNote
from django.utils import timezone
from django.db.models import Q
from django.http import JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .forms import TaskForm, RegisterForm


def auth_view(request):
    if request.user.is_authenticated:
        return redirect('home')

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
    profile, _ = UserProfile.objects.get_or_create(user=request.user)

    tasks = Task.objects.filter(
        user=request.user
    ).filter(
        Q(task_type=Task.TASK_DAILY) |
        Q(task_type=Task.TASK_WEEKLY) |
        Q(task_type=Task.TASK_ONCE, date=today)
    )

    if request.method == "POST":
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.user = request.user
            task.save()
        return redirect('home')

    tasks_list = list(tasks)
    tasks_total = len(tasks_list)
    tasks_done = sum(1 for t in tasks_list if t.is_done_today())
    day_progress = int((tasks_done / tasks_total) * 100) if tasks_total > 0 else 0

    context = {
        'tasks': tasks_list,
        'form': form,
        'profile': profile,
        'rank_icon': profile.rank()[0],
        'rank_name': profile.rank()[1],
        'progress': profile.rank_progress_percent(),
        'xp_to_next': profile.xp_to_next_rank(),
        'tasks_total': tasks_total,
        'tasks_done': tasks_done,
        'day_progress': day_progress,
    }
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
    profile, _ = UserProfile.objects.get_or_create(user=request.user)

    if task.task_type == Task.TASK_ONCE:
        if not task.completed:
            task.once_task()
            profile.xp += 10
            profile.save()

    elif task.task_type == Task.TASK_DAILY:
        today = timezone.localdate()
        if task.last_completed != today:
            task.daily_task()
            profile.xp += 15
            if task.streak > 0 and task.streak % 7 == 0:
                profile.xp += 20
            if task.streak > 0 and task.streak % 30 == 0:
                profile.xp += 50
            profile.save()
        else:
            task.daily_task()

    elif task.task_type == Task.TASK_WEEKLY:
        was_done = task.is_done_today()
        task.weekly_task()
        if not was_done:
            profile.xp += 25
        else:
            profile.xp = max(0, profile.xp - 25)
        profile.save()

    return redirect('home')


# ============================================================
# Kalendarz
# ============================================================

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


# ============================================================
# Notatki
# ============================================================

@login_required(login_url='auth')
def note_list(request, task_id):
    """GET — zwraca listę notatek dla danego zadania."""
    task = get_object_or_404(Task, pk=task_id, user=request.user)
    notes = list(task.notes.values('id', 'title', 'content', 'created_at'))
    # serializuj daty
    for n in notes:
        n['created_at'] = n['created_at'].strftime('%d.%m.%Y %H:%M')
    return JsonResponse({'notes': notes})


@login_required(login_url='auth')
def note_save(request, task_id):
    """POST — zapisuje nową notatkę do zadania."""
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'msg': 'Method not allowed'}, status=405)

    task = get_object_or_404(Task, pk=task_id, user=request.user)
    title = request.POST.get('title', '').strip()
    content = request.POST.get('content', '').strip()

    if not title:
        return JsonResponse({'status': 'error', 'msg': 'Tytuł jest wymagany'}, status=400)

    note = TaskNote.objects.create(task=task, title=title, content=content)
    return JsonResponse({'status': 'ok', 'id': note.id})


@login_required(login_url='auth')
def note_delete(request, note_id):
    """POST — usuwa notatkę."""
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'msg': 'Method not allowed'}, status=405)

    note = get_object_or_404(TaskNote, pk=note_id, task__user=request.user)
    note.delete()
    return JsonResponse({'status': 'ok'})


# ============================================================
# Profil
# ============================================================

@login_required(login_url='auth')
def profile_view(request):
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    total_tasks = Task.objects.filter(user=request.user, completed=True).count()
    longest_streak = Task.objects.filter(
        user=request.user, task_type=Task.TASK_DAILY
    ).order_by('-streak').first()

    context = {
        'profile': profile,
        'rank_icon': profile.rank()[0],
        'rank_name': profile.rank()[1],
        'progress': profile.rank_progress_percent(),
        'xp_to_next': profile.xp_to_next_rank(),
        'total_tasks': total_tasks,
        'longest_streak': longest_streak.streak if longest_streak else 0,
    }
    return render(request, 'ToDo/profile.html', context)