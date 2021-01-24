from django.urls import path
from chemapp import views


app_name = 'chemapp'

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('courses/', views.courses, name='courses'),
    path('courses/add_course/',views.add_course, name='add_course'),
    path('courses/<slug:course_name_slug>/', views.course, name='course'),
    path('courses/<slug:course_name_slug>/add_assessments/', views.add_assessments, name='add_assessments'),
    path('courses/<slug:course_name_slug>/add_assessmentComponents/', views.add_assessmentComponents, name='add_assessmentComponents'),
    path('student/', views.student, name='student'),
    path('student/add_student/', views.add_student, name='add_student'),
    path('student/upload_student_csv/', views.upload_student_csv, name='upload_student_csv'),

    
]
