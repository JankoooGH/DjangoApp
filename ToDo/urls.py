from django.urls import path
from . import views

urlpatterns = [
    path('', views.landing, name='landing'),       # ← nowy landing page
    path('dashboard/', views.home, name='home'),   # ← dashboard
    path('auth/', views.auth_view, name='auth'),
    path('logout/', views.logout_view, name='logout'),
    path('delete/<int:task_id>/', views.delete_task, name='delete_task'),
    path('toggle/<int:task_id>/', views.toggle_task, name='toggle_task'),
]