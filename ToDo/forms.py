from django import forms
from .models import Task
from django.utils import timezone


class TaskForm(forms.ModelForm):
    date = forms.DateField(
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

        return cleaned_data

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['weekly_target'].required = False
