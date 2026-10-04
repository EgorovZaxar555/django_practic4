from django.urls import path
from . import views

app_name = 'main_practic'

urlpatterns = [
    path('student/', views.student_page, name='student-page'),
    path('teacher/', views.teacher_page, name='teacher-page'),
    path('no-profile/', views.no_profile_page, name='no-profile'),
    path('upload/', views.upload_raw, name='upload-raw'),
    path('avatar/', views.student_avatar_update, name='avatar-update'),
    path('students/', views.student_list, name='student-list'),
]