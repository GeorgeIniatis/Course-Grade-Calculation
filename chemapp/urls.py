from django.urls import path
from chemapp import views

app_name = 'chemapp'

urlpatterns = [
    path('', views.index, name='home'),
    path('about/', views.about, name='about'),
    path('category/<slug:category_name_slug>/',views.show_category, name='show_category'),
    path('register/', views.user_registration, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
]
