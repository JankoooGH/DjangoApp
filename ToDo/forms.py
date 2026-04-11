
from django import forms
from .models import Task
from django.utils import timezone
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']


class TaskForm(forms.ModelForm):
    date = forms.DateField(
        required=False,
        input_formats=['%d.%m.%Y'],
        widget=forms.DateInput(attrs={'placeholder': 'dd.mm.yyyy'})
    )

    class Meta:
        model = Task
        fields = ['title', 'task_type', 'date', "weekly_target"]

    def clean(self):
        cleaned_data = super().clean()
        task_type = cleaned_data.get("task_type")
        date = cleaned_data.get("date")

        if task_type == Task.TASK_ONCE and not date:
            cleaned_data["date"] = timezone.localdate()

        # if task_type == Task.TASK_ONCE:


        return cleaned_data

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['weekly_target'].required = False
