from django.shortcuts import render, redirect, get_object_or_404
from .models import Task
from .forms import TaskForm


def home(request):
    tasks = Task.objects.all()
    form = TaskForm()

    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            form.save()
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
    if request.method == "POST":
        task.completed = not task.completed
        task.count_streak()
        task.save()
    return redirect('home')
