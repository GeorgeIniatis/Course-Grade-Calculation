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
from django.template.defaultfilters import slugify

@login_required
def home(request):
    context_dict = {'boldmessage':'This is the home page'}
    return render(request,'chemapp/home.html', context=context_dict)

@login_required
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

    components = []

    if (request.method == 'POST'):
        course_form = CourseForm(request.POST)
        
        if course_form.is_valid():
            course = course_form.save()
            course_slug = course.slug
            return redirect(reverse('chemapp:add_assessments',kwargs={'course_name_slug':course_slug}))
        
        else:
            print(course_form.errors)
    else:
        course_form = CourseForm()
        
    addCourseDict['course_form'] = CourseForm()
    
    return render(request,'chemapp/add_course.html',context = addCourseDict)

@login_required
def add_assessments(request,course_name_slug):
    addAssessmentsDict = {}
    addAssessmentsDict['course_name_slug'] = course_name_slug

    AssessmentFormSet = formset_factory(AssessmentForm,extra=1)
    course = Course.objects.get(slug = course_name_slug)
    
    if (request.method == 'POST'):
        assessment_formset = AssessmentFormSet(request.POST)
        
        if assessment_formset.is_valid():
            assessments = []
            weightSum = 0
            for form in assessment_formset:
                weight = form.cleaned_data.get('weight')
                weightSum += weight
                name = form.cleaned_data.get('assessmentName')
                marks = form.cleaned_data.get('totalMarks')
                dueDate = form.cleaned_data.get('dueDate')
                slug = slugify(name)

                assessments.append(Assessment(weight=weight,
                                              assessmentName=name,
                                              totalMarks=marks,
                                              dueDate=dueDate,
                                              course=course,
                                              slug=slug))
                
            if weightSum != 1:
                messages.error(request, 'The sum of the Assessment Weights must be equal to 1')
                return redirect(reverse('chemapp:add_assessments',kwargs={'course_name_slug':course_name_slug}))
            else:
                Assessment.objects.bulk_create(assessments)
                assessmentsCreated = Assessment.objects.filter(course=course)
                
                assessment_name_slug = assessmentsCreated.first().slug
                return redirect(reverse('chemapp:add_assessmentComponents',kwargs={'course_name_slug':course_name_slug,'assessment_name_slug':assessment_name_slug}))
        else:
            print(assessment_formset.errors)
    else:
        assessment_formset = AssessmentFormSet()
        
    addAssessmentsDict['assessment_formset'] = assessment_formset
    
    return render(request,'chemapp/add_assessments.html',context = addAssessmentsDict)

@login_required
def add_assessmentComponents(request,course_name_slug,assessment_name_slug):
    addAssessmentComponentsDict = {}
    addAssessmentComponentsDict['course_name_slug'] = course_name_slug
    addAssessmentComponentsDict['assessment_name_slug'] = assessment_name_slug
    addAssessmentComponentsDict['allComponentsAdded'] = False
    
    AssessmentComponentFormSet = formset_factory(AssessmentComponentForm,extra=1)
    course = Course.objects.get(slug = course_name_slug)
    allAssessments = Assessment.objects.filter(course=course)
    assessment = Assessment.objects.get(course=course,slug=assessment_name_slug)
    
    addAssessmentComponentsDict['assessment'] = assessment.assessmentName

    if (request.method == 'POST'):
        assessmentComponent_formset = AssessmentComponentFormSet(request.POST)
        
        if assessmentComponent_formset.is_valid():
            assessmentComponents = []
            
            for form in assessmentComponent_formset:
                required = form.cleaned_data.get('required')
                marks = form.cleaned_data.get('marks')
                description = form.cleaned_data.get('description')
 
                assessmentComponents.append(AssessmentComponent(required=required,
                                              marks=marks,
                                              description=description,
                                              assessment=assessment))
                
            AssessmentComponent.objects.bulk_create(assessmentComponents)
            assessment.componentsAdded = True
            assessment.save()

            for assessment in allAssessments:
                if assessment.componentsAdded == False:
                    assessment_name_slug = assessment.slug
                    return redirect(reverse('chemapp:add_assessmentComponents',kwargs={'course_name_slug':course_name_slug,'assessment_name_slug':assessment_name_slug}))

            addAssessmentComponentsDict['allComponentsAdded'] = True
            
        else:
            print(assessmentComponent_formset.errors)
    else:
        assessmentComponent_formset = AssessmentComponentFormSet()
        
    addAssessmentComponentsDict['assessmentComponent_formset'] = assessmentComponent_formset
    
    return render(request,'chemapp/add_assessmentComponents.html',context = addAssessmentComponentsDict)

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
def students(request):
    context ={}

    Students = Student.objects.all()

    return render(request, 'chemapp/students.html',locals())

@login_required
def add_student(request):
    addStudentDict = {}
    addStudentDict['studentAdded'] = False

    if request.method == 'POST':
        student_form = StudentForm(request.POST)
        if student_form.is_valid():
            student = student_form.save(commit=False)
            #Just to test until we have correct equation
            student.anonID = 0000000
            student.save()
            
            degree = Degree.objects.get(degreeCode=student.academicPlan)
            student.courses.set(Course.objects.filter(degree=degree,year=student.currentYear))
            student.save()
            
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
