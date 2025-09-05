from django.shortcuts import render, redirect, get_object_or_404
from .models import Task
from .forms import TaskForm


def home(request):
    return render(request, 'ToDo/home.html')


#Logika aplikacji do zrobienia
