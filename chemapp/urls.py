from django.urls import path
from chemapp import views
from django.contrib import admin
from django.conf.urls import url

admin.autodiscover()
admin.site.enable_nav_sidebar = False

app_name = 'chemapp'

urlpatterns = [
    path('', views.user_login, name='login'),
    path('home/', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('logout/', views.user_logout, name='logout'),
    path('degrees/', views.degrees, name='degrees'),
    path('degrees/upload_degree_csv/', views.upload_degree_csv, name='upload_degree_csv'),
    path('degrees/add_degree/', views.add_degree, name='add_degree'),
    path('courses/', views.courses, name='courses'),
    path('courses/add_course/',views.add_course, name='add_course'),
    path('courses/add_course/<slug:course_name_slug>/',views.course_lecturer, name='course_lecturer'),
    path('courses/upload_course_csv/', views.upload_course_csv, name='upload_course_csv'),
    path('courses/<slug:course_name_slug>/', views.course, name='course'),
    path('courses/<slug:course_name_slug>/edit_course/', views.edit_course, name='edit_course'),
    path('courses/<course_code>/upload_assessment_csv/', views.upload_assessment_csv, name='upload_assessment_csv'),
    path('courses/<slug:course_name_slug>/add_assessments/', views.add_assessments, name='add_assessments'),
    path('courses/<slug:course_name_slug>/<slug:assessment_name_slug>/add_assessmentComponents/', views.add_assessmentComponents, name='add_assessmentComponents'),
    path('courses/<course_code>/<assessment_name>/upload_assessment_comp_csv/', views.upload_assessment_comp_csv, name='upload_assessment_comp_csv'),
    path('staff/', views.staff, name='staff'),
    path('staff/add_staff/', views.add_staff, name='add_staff'),
    path('staff/<staffID>/', views.staff_member, name='staff_member'),
    path('staff/<staffID>/edit_staff/', views.edit_staff, name='edit_staff'),
    path('students/', views.students, name='students'),
    path('students/add_student/', views.add_student, name='add_student'),
    path('students/upload_student_csv/', views.upload_student_csv, name='upload_student_csv'),
    path('students/<student_id>/', views.student, name='student'),
    path('students/<student_id>/<slug:course_name_slug>/<slug:assessment_name_slug>/add_grades/', views.add_grades, name='add_grades'),
    path('students/<student_id>/<slug:course_name_slug>/<slug:assessment_name_slug>/add_final_grade/', views.add_final_grade, name='add_final_grade'),
    path('search/', views.search_course, name='search_course'),
]
