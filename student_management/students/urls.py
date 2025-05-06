from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('add/', views.add_students, name='add_students'),
    path('edit/<int:pk>/', views.edit_students, name='edit_students'),
    path('delete/<int:pk>/', views.delete_students, name='delete_students'),
    path('students/<int:pk>/', views.view_students, name='view_students'),
    path('predict-course/', views.predict_course, name='predict_course'),
]
