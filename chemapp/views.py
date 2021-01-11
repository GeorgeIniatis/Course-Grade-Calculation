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

@login_required
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

@login_required
def course(request,course_name_slug):
    courseDict = {}
    try:
        course = Course.objects.get(slug=course_name_slug)
        assessments = Assessment.objects.filter(course=course)
        courseDict['course'] = course
        courseDict['assessments'] = assessments
    except Course.DoesNotExist:
        raise Http404("Course does not exist")
    
    return render(request,'chemapp/course.html', context=courseDict)

@login_required
def add_course(request):
    addCourseDict = {}
    addCourseDict['courseAdded'] = False
    
    if request.method == 'POST':
        course_form = CourseForm(request.POST)
        assessment_form = AssessmentForm(request.POST)

        if course_form.is_valid() and assessment_form.is_valid():
            course_form.save()
            courseName = (request.POST['shortHand']).upper()
            course = Course.objects.get(shortHand=courseName)
            
            assessment = assessment_form.save(commit=False)
            assessment.course = course
            assessment.save()
            
            addCourseDict['courseAdded'] = True
        else:
            print(course_form.errors, assessment_form.errors)
    else:
        course_form = CourseForm()
        assessment_form = AssessmentForm()
        
    addCourseDict['course_form'] = course_form
    addCourseDict['assessment_form'] = assessment_form
    
    return render(request,'chemapp/add_course.html',context = addCourseDict)
       
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
