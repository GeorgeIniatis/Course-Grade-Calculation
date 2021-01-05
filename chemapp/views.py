from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from chemapp.models import *
from chemapp.forms import *
from django.http import Http404

def home(request):
    context_dict = {'boldmessage':'This is the home page'}
    return render(request,'chemapp/home.html', context=context_dict)

def about(request):
    context_dict = {'boldmessage':'This is the about page'}
    return render(request,'chemapp/home.html', context=context_dict)

def courses(request):
    coursesDict = {}
    courses = Course.objects.all()

    for course in courses:
        name = course.name
        year = course.year
        slug = course.slug

        courseList = [year,slug]

        coursesDict[name] = courseList

    return render(request,'chemapp/courses.html', {'courses': coursesDict})

def course(request,course_name_slug):
    courseDict = {}
    try:
        course = Course.objects.get(slug=course_name_slug)
        assessments = Assessment.objects.filter(course=course)
        courseDict['course'] = course
        courseDict['assessments'] = assessments
    except Course.DoesNotExist:
        raise Http404("Course does not exist")
    except Assessment.DoesNotExist:
        courseDict['assessments'] = None

    return render(request,'chemapp/course.html', context=courseDict)
        
def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)
        if user:
            if user.is_active:
                login(request, user)
                return redirect(reverse('chemapp:home'))
            else:
                messages.error(request, 'Your account is disabled')
                return redirect(reverse('chemapp:login'))
        else:
            messages.error(request, 'Incorrect username or password')
            return redirect(reverse('chemapp:login'))
    else:
        return render(request, 'chemapp/login.html')

@login_required
def user_logout(request):
    logout(request)
    return redirect(reverse('chemapp:home'))
