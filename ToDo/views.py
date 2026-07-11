from django.shortcuts import render, redirect, get_object_or_404
from .models import Task, UserProfile, TaskNote, TaskLog
from django.utils import timezone
from django.db.models import Q
from django.http import JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .forms import TaskForm, RegisterForm
from django.db.models import Count
from django.utils.dateparse import parse_date


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

    longest_streak_task = Task.objects.filter(
        user=request.user, task_type=Task.TASK_DAILY
    ).order_by('-streak').first()
    longest_streak = longest_streak_task.streak if longest_streak_task else 0

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
        'today': timezone.localdate(),
        'longest_streak': longest_streak,
    }
    return render(request, 'ToDo/main.html', context)

def landing(request):
    if request.user.is_authenticated:
        return redirect('home')
    return render(request, 'ToDo/home.html')

def delete_task(request, task_id):
    task = get_object_or_404(Task, pk=task_id, user=request.user)
    if request.method == "POST":
        task.delete()
        return redirect('habbits')

def toggle_task(request, task_id):
    task = get_object_or_404(Task, pk=task_id, user=request.user)
    profile, _ = UserProfile.objects.get_or_create(user=request.user)

    if task.task_type == Task.TASK_ONCE:
        if not task.completed:
            task.once_task()
            profile.xp += 10
            TaskLog.objects.get_or_create(task=task, date=task.date, defaults={"completed": True})
        else:
            task.completed = False
            task.save()
            profile.xp = max(0, profile.xp - 10)
            TaskLog.objects.filter(task=task, date=task.date).delete()
        profile.save()

    elif task.task_type == Task.TASK_DAILY:
        today = timezone.localdate()
        if task.last_completed != today:
            task.daily_task()
            profile.xp += 15
            TaskLog.objects.get_or_create(task=task, date=today, defaults={"completed": True})
            if task.streak > 0 and task.streak % 7 == 0:
                profile.xp += 20
            if task.streak > 0 and task.streak % 30 == 0:
                profile.xp += 50
        else:
            task.last_completed = None
            task.streak = max(0, task.streak - 1)
            task.save()
            profile.xp = max(0, profile.xp - 15)
            TaskLog.objects.filter(task=task, date=today).delete()
        profile.save()

    elif task.task_type == Task.TASK_WEEKLY:
        was_done = task.is_done_today()
        task.weekly_task()
        if not was_done:
            profile.xp += 25
        else:
            profile.xp = max(0, profile.xp - 25)
        profile.save()

    all_tasks = list(Task.objects.filter(
        user=request.user
    ).filter(
        Q(task_type=Task.TASK_DAILY) |
        Q(task_type=Task.TASK_WEEKLY) |
        Q(task_type=Task.TASK_ONCE, date=timezone.localdate())
    ))
    tasks_total = len(all_tasks)
    tasks_done = sum(1 for t in all_tasks if t.is_done_today())
    day_progress = int((tasks_done / tasks_total) * 100) if tasks_total > 0 else 0

    if task.task_type == Task.TASK_DAILY:
        streak = task.streak
    elif task.task_type == Task.TASK_WEEKLY:
        streak = task.weekly_progress_count()
    else:
        streak = None

    return JsonResponse({
        'status': 'ok',
        'is_done': task.is_done_today(),
        'day_progress': day_progress,
        'tasks_done': tasks_done,
        'tasks_total': tasks_total,
        'xp': profile.xp,
        'weekly_progress': task.weekly_progress_count() if task.task_type == Task.TASK_WEEKLY else None,
        'weekly_streak': task.weekly_streak() if task.task_type == Task.TASK_WEEKLY else None,
        'streak': task.streak if task.task_type == Task.TASK_DAILY else None,
        'weekly_target': task.weekly_target,
    })

def main(request):
    return render(request, 'ToDo/main.html')


# ============================================================
# Kalendarz
# ============================================================

@login_required(login_url='auth')
def calendar_view(request):
    profile, _ = UserProfile.objects.get_or_create(user=request.user)

    context = {
        'profile': profile,
        'rank_icon': profile.rank()[0],
        'rank_name': profile.rank()[1],
        'progress': profile.rank_progress_percent(),
        'xp_to_next': profile.xp_to_next_rank(),
    }

    return render(request, "ToDo/calendar.html", context)


def calendar_events(request):
    events = []
    tasks = Task.objects.filter(user=request.user)
    for task in tasks:
        if task.date:
            events.append({
                "title": task.title,
                "start": task.date.isoformat(),
            })
    return JsonResponse(events, safe=False)

@login_required
def calendar_month(request):
    year = request.GET.get('year')
    month = request.GET.get('month')
    logs = TaskLog.objects.filter(
        task__user=request.user,
        date__year=year,
        date__month=month,
        completed=True
    ).values('date').annotate(count=Count('id'))

    data = {}
    for log in logs:
        data[log['date'].isoformat()] = log['count']

    return JsonResponse(data)

@login_required
def calendar_day(request):
    date = request.GET.get('date')
    parsed_date = parse_date(date)

    tasks = Task.objects.filter(
        user=request.user
    ).filter(
        Q(task_type=Task.TASK_DAILY) |
        Q(task_type=Task.TASK_WEEKLY) |
        Q(task_type=Task.TASK_ONCE, date=parsed_date)
    )

    data = []
    for task in tasks:
        is_completed = task.logs.filter(date=parsed_date, completed=True).exists()
        data.append({
            'title': task.title,
            'type': task.task_type,
            'color': task.color,
            'completed': is_completed,
            'xp': 25 if task.task_type == 'WEEKLY' else 15 if task.task_type == 'DAILY' else 10,
        })

    return JsonResponse(data, safe=False)


# ============================================================
# Notatki
# ============================================================

@login_required(login_url='auth')
def note_list(request, task_id):
    """GET — zwraca listę notatek dla danego zadania."""
    task = get_object_or_404(Task, pk=task_id, user=request.user)
    notes = list(task.notes.values('id', 'title', 'content', 'created_at'))
    # serializer daty
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

    longest_streak_task = Task.objects.filter(
        user=request.user, task_type=Task.TASK_DAILY
    ).order_by('-streak').first()

    daily_count  = Task.objects.filter(user=request.user, task_type=Task.TASK_DAILY).count()
    weekly_count = Task.objects.filter(user=request.user, task_type=Task.TASK_WEEKLY).count()
    once_count   = Task.objects.filter(user=request.user, task_type=Task.TASK_ONCE).count()
    total_all    = daily_count + weekly_count + once_count

    total_tasks = TaskLog.objects.filter(
        task__user=request.user, completed=True
    ).count()

    active_days = TaskLog.objects.filter(
        task__user=request.user, completed=True
    ).values('date').distinct().count()

    context = {
        'profile': profile,
        'rank_icon': profile.rank()[0],
        'rank_name': profile.rank()[1],
        'progress': profile.rank_progress_percent(),
        'xp_to_next': profile.xp_to_next_rank(),
        'total_tasks': total_tasks,
        'longest_streak': longest_streak_task.streak if longest_streak_task else 0,
        'daily_count': daily_count,
        'weekly_count': weekly_count,
        'once_count': once_count,
        'total_all': total_all,
        'active_days': active_days,
    }
    return render(request, 'ToDo/profile.html', context)

@login_required(login_url='auth')
def habbits(request):
    today = timezone.localdate()
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    form = TaskForm()

    tasks = Task.objects.filter(user=request.user).filter(
        Q(task_type=Task.TASK_DAILY) |
        Q(task_type=Task.TASK_WEEKLY) |
        Q(task_type=Task.TASK_ONCE, date=today)
    )

    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.user = request.user
            task.save()
        return redirect('habbits')

    context = {
        'tasks': tasks,
        'form': form,
        'profile': profile,
        'rank_icon': profile.rank()[0],
        'rank_name': profile.rank()[1],
        'progress': profile.rank_progress_percent(),
        'xp_to_next': profile.xp_to_next_rank(),
    }
    return render(request, 'ToDo/habbits.html', context)