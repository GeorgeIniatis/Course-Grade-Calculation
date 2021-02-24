from django.urls import path
from chemapp import views
from django.contrib import admin

admin.autodiscover()
admin.site.enable_nav_sidebar = False

app_name = 'chemapp'

urlpatterns = [
    path('', views.user_login, name='login'),
    path('home/', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('logout/', views.user_logout, name='logout'),

    # Degree URLs
    path('degrees/', views.degrees, name='degrees'),
    path('degrees/add_degree/', views.add_degree, name='add_degree'),
    path('degrees/upload_degree_csv/', views.upload_degree_csv, name='upload_degree_csv'),
    path('degrees/<slug:degree_code_slug>/edit_degree', views.edit_degree, name='edit_degree'),
    path('degrees/<slug:degree_code_slug>/delete_degree', views.delete_degree, name='delete_degree'),

    # Course URLs
    path('courses/', views.courses, name='courses'),
    path('courses/add_course/',views.add_course, name='add_course'),
    path('courses/upload_course_csv/', views.upload_course_csv, name='upload_course_csv'),
    path('courses/<slug:course_name_slug>/', views.course, name='course'),
    path('courses/<slug:course_name_slug>/edit_course/', views.edit_course, name='edit_course'),
    path('courses/<slug:course_name_slug>/delete_course/', views.delete_course, name='delete_course'),
    path('courses/<slug:course_name_slug>/upload_student_csv/', views.upload_student_csv, name='upload_student_csv'),

    # Assessment URLs
    path('courses/<slug:course_name_slug>/add_assessments/', views.add_assessments, name='add_assessments'),
    path('courses/<slug:course_name_slug>/upload_assessment_csv/', views.upload_assessment_csv, name='upload_assessment_csv'),
    path('courses/<slug:course_name_slug>/<slug:assessment_name_slug>/edit_assessment/', views.edit_assessment, name='edit_assessment'),
    path('courses/<slug:course_name_slug>/<slug:assessment_name_slug>/delete_assessment/', views.delete_assessment, name='delete_assessment'),

    # Assessment Component URLs
    path('courses/<slug:course_name_slug>/<slug:assessment_name_slug>/add_assessmentComponents/', views.add_assessmentComponents, name='add_assessmentComponents'),
    path('courses/<slug:course_name_slug>/<slug:assessment_name_slug>/upload_assessment_comp_csv/', views.upload_assessment_comp_csv, name='upload_assessment_comp_csv'),
    path('courses/<slug:course_name_slug>/<slug:assessment_name_slug>/<slug:assessment_component_slug>/edit_component/', views.edit_assessmentComponent, name='edit_assessmentComponent'),
    path('courses/<slug:course_name_slug>/<slug:assessment_name_slug>/<slug:assessment_component_slug>/delete_component/', views.delete_assessmentComponent, name='delete_assessmentComponent'),
 	path('courses/<slug:course_name_slug>/<slug:assessment_name_slug>/<slug:assessment_component_slug>/upload_grades_csv/', views.upload_grades_csv, name='upload_grades_csv'),
    
    # Student URLs
    path('students/', views.students, name='students'),
    path('students/add_student/', views.add_student, name='add_student'),
    path('ajax/filter-courses/', views.ajax_filter_courses, name='ajax_filter_courses'),
    #path('students/upload_student_csv/', views.upload_student_csv, name='upload_student_csv'),
    path('students/<student_id>/', views.student, name='student'),
    path('students/<student_id>/edit_student/', views.edit_student, name='edit_student'),
    path('students/<student_id>/delete_student/', views.delete_student, name='delete_student'),

    # Student Grades URLs
    path('students/<student_id>/<slug:course_name_slug>/<slug:assessment_name_slug>/add_grades/', views.add_grades, name='add_grades'),
    path('students/<student_id>/<slug:course_name_slug>/<slug:assessment_name_slug>/edit_grades/', views.edit_grades, name='edit_grades'),
    path('students/<student_id>/<slug:course_name_slug>/<slug:assessment_name_slug>/delete_grades/', views.delete_grades, name='delete_grades'),
    path('students/<student_id>/<slug:course_name_slug>/<slug:assessment_name_slug>/add_final_grade/', views.add_final_grade, name='add_final_grade'),
    path('students/<student_id>/<slug:course_name_slug>/<slug:assessment_name_slug>/edit_final_grade/', views.edit_final_grade, name='edit_final_grade'),
    path('students/<student_id>/<slug:course_name_slug>/<slug:assessment_name_slug>/delete_final_grade/', views.delete_final_grade, name='delete_final_grade'),
]
