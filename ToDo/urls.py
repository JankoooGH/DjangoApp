from django.urls import path
from . import views

urlpatterns = [
    path('', views.landing, name='landing'),
    path('dashboard/', views.home, name='home'),
    path('auth/', views.auth_view, name='auth'),
    path('profile/', views.profile_view, name='profile'),
    path('logout/', views.logout_view, name='logout'),
    path('delete/<int:task_id>/', views.delete_task, name='delete_task'),
    path('toggle/<int:task_id>/', views.toggle_task, name='toggle_task'),

    # Notatki
    path('note/<int:task_id>/list/', views.note_list, name='note_list'),
    path('note/<int:task_id>/save/', views.note_save, name='note_save'),
    path('note/<int:note_id>/delete/', views.note_delete, name='note_delete'),
]
