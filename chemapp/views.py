from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from chemapp.models import *
from chemapp.forms import *
from django.http import Http404
from django.shortcuts import get_object_or_404
import csv, io
from django.forms.formsets import formset_factory

def home(request):
    context_dict = {'boldmessage':'This is the home page'}
    return render(request,'chemapp/home.html', context=context_dict)

def about(request):
    context_dict = {'boldmessage':'This is the about page'}
    return render(request,'chemapp/about.html', context=context_dict)

@login_required
def courses(request):
    coursesDict = {}
    courses = Course.objects.all()

    for course in courses:
        year = course.year
        slug = course.slug
        name = course.name
        color = course.courseColor
    
        courseList = [year,slug,name,color]

        coursesDict[course] = courseList

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

    AssessmentFormSet = formset_factory(AssessmentForm,extra=1)

    if request.method == 'POST':
        course_form = CourseForm(request.POST)
        assessment_formset = AssessmentFormSet(request.POST)
        
        if course_form.is_valid() and assessment_formset.is_valid():
            course = course_form.save()
            
            newAssessments = []
            weightSum = 0
            for form in assessment_formset:
                weight = form.cleaned_data.get('weight')
                weightSum += weight
                name = form.cleaned_data.get('assessmentName')
                marks = form.cleaned_data.get('totalMarks')
                dueDate = form.cleaned_data.get('dueDate')

                newAssessments.append(Assessment(weight=weight,
                                                 assessmentName=name,
                                                 totalMarks=marks,
                                                 dueDate=dueDate,
                                                 course=course))

            if weightSum > 1:
                course.delete()
                messages.error(request, 'The sum of the Assessment Weights must be less than 1')
                return redirect(reverse('chemapp:add_course'))
            else:
                Assessment.objects.bulk_create(newAssessments)
                addCourseDict['courseAdded'] = True
        else:
            print(course_form.errors,assessment_formset.errors)
    else:
        course_form = CourseForm()
        assessment_formset = AssessmentFormSet()

    addCourseDict['course_form'] = course_form
    addCourseDict['assessment_formset'] = assessment_formset

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

@login_required
def student(request):
    context ={}

    Students = Student.objects.all()

    return render(request, 'chemapp/student.html',locals())

@login_required
def add_student(request):
	addStudentDict = {}
	addStudentDict['studentAdded'] = False
	if request.method == 'POST':
		student_form = StudentForm(request.POST)
		if student_form.is_valid():
			student_form.save()
			addStudentDict['studentAdded'] = True
		else:
			print(student_form.errors)
	else:
			student_form = StudentForm()
	addStudentDict['student_form'] = student_form
	return render(request,'chemapp/add_student.html',context=addStudentDict)

@login_required
def upload_student_csv(request):
    #student_dict = {'boldmessage':'Upload csv file to add students'}
    #return render(request,'chemapp/upload_student_csv.html', context=student_dict)
    template='chemapp/upload_student_csv.html'
    data=Student.objects.all()

    prompt={'Order':'studentID,firstName,lastName,academicPlan,anonID,currentYear', 'students':data}
    if request.method == "GET":
    	return render(request, template, prompt)

    csv_file =request.FILES['file']
    if not csv_file.name.endswith('.csv'):
    	messages.error(request, 'THIS IS NOT A CSV FILE')

    data_set =csv_file.read().decode('UTF-8')
    io_string = io.StringIO(data_set)
    next(io_string)
    for column in csv.reader(io_string,delimiter=',',quotechar="|"):
    	_, created = Student.objects.update_or_create(
    		firstName= column[0],
    		lastName= column[1],
    		studentID= column[2],
    		anonID=column[2],
    		academicPlan=column[3],
    		currentYear=column[4],
    		#graduationDate=column[5],
    	)
    context={}
    return render(request,template,context)
