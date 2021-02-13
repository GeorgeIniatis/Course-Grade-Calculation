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
import random

GRADE_TO_BAND = {22: 'A1', 21: 'A2', 20: 'A3', 19: 'A4', 18: 'A5',
                 17: 'B1', 16: 'B2', 15: 'B3',
                 14: 'C1', 13: 'C2', 12: 'C3',
                 11: 'D1', 10: 'D2', 9: 'D3',
                 8: 'E1', 7: 'E2', 6: 'E3',
                 5: 'F1', 4: 'F2', 3: 'F3',
                 2: 'G1', 1: 'G2', 0: 'G3',
                 }


@login_required
def home(request):
    context_dict = {'boldmessage': 'This is the home page'}
    return render(request, 'chemapp/home.html', context=context_dict)


@login_required
def about(request):
    context_dict = {'boldmessage': 'This is the about page'}
    return render(request, 'chemapp/about.html', context=context_dict)


@login_required
def degrees(request):
    degreesDict = {}

    degrees = Degree.objects.all()
    degreesDict['degrees'] = degrees

    return render(request, 'chemapp/degrees.html', context=degreesDict)


@login_required
def add_degree(request):
    addDegreeDict = {}

    DegreeFormSet = formset_factory(DegreeForm, extra=1)

    if (request.method == 'POST'):
        degree_formset = DegreeFormSet(request.POST)

        if degree_formset.is_valid():
            degrees = []

            # This is used to check for Degree duplicates
            codes = []
            for form in degree_formset:
                degreeCode = form.cleaned_data.get('degreeCode')
                name = form.cleaned_data.get('name')

                if degreeCode in codes:
                    messages.error(request, "Duplicate degree " + degreeCode + " was only added once")
                else:
                    codes.append(degreeCode)
                    degrees.append(Degree(degreeCode=degreeCode,
                                          name=name,
                                          numberOfCourses=0,
                                          numberOfStudents=0))

            Degree.objects.bulk_create(degrees)

            messages.success(request, "Degrees Added Successfully")
            return redirect(reverse('chemapp:degrees'))
        else:
            print(degree_formset.errors)

    else:
        degree_formset = DegreeFormSet()

    addDegreeDict['degree_formset'] = degree_formset

    return render(request, 'chemapp/add_degree.html', context=addDegreeDict)


@login_required
def courses(request):
    coursesDict = {}
    courses = Course.objects.all()

    yearDict = {}

    for course in courses:
        year = course.year
        slug = course.slug
        name = course.name
        color = course.courseColor
        level = course.level

        if year not in yearDict.values():
            yearDict[year] = year

        courseList = [year, slug, name, color, level]

        coursesDict[course] = courseList

    return render(request, 'chemapp/courses.html', {'courses': coursesDict, 'years': yearDict})


# Dictionary structure
# courseDict = {'course':courseObject,
#               'assessments':{assessmentObject1:[componentObject1,componentObject2],
#                              assessmentObject2:[componentObject3,componentObject4]},
#              }
@login_required
def course(request, course_name_slug):
    courseDict = {}
    try:
        course = Course.objects.get(slug=course_name_slug)
        assessments = Assessment.objects.filter(course=course)
        courseDict['course'] = course
        courseDict['assessments'] = {}

        for assessment in assessments:
            courseDict['assessments'][assessment] = []
            components = AssessmentComponent.objects.filter(assessment=assessment)

            for component in components:
                courseDict['assessments'][assessment].append(component)

    except Course.DoesNotExist:
        raise Http404("Course does not exist")

    return render(request, 'chemapp/course.html', context=courseDict)


@login_required
def add_course(request):
    addCourseDict = {}

    if (request.method == 'POST'):
        course_form = CourseForm(request.POST)

        if course_form.is_valid():
            code = course_form.cleaned_data.get('code').upper()
            degree = course_form.cleaned_data.get('degree')

            # Check if Course has already been added
            try:
                course = Course.objects.get(code=code, degree=degree)
                messages.error(request, 'Course has already been added!')
                return redirect(reverse('chemapp:add_course'))
            except Course.DoesNotExist:
                pass

            course = course_form.save()
            course_slug = course.slug

            # Increment degree course count
            degree = course.degree
            degree.numberOfCourses = degree.numberOfCourses + 1
            degree.save()

            return redirect(reverse('chemapp:add_assessments', kwargs={'course_name_slug': course_slug}))

        else:
            messages.error(request, 'Course has already been added!')
            print(course_form.errors)
    else:
        course_form = CourseForm()

    addCourseDict['course_form'] = CourseForm()

    return render(request, 'chemapp/add_course.html', context=addCourseDict)


@login_required
def add_assessments(request, course_name_slug):
    addAssessmentsDict = {}
    addAssessmentsDict['course_name_slug'] = course_name_slug

    AssessmentFormSet = formset_factory(AssessmentForm, extra=1)
    course = Course.objects.get(slug=course_name_slug)

    if (request.method == 'POST'):
        assessment_formset = AssessmentFormSet(request.POST)

        if assessment_formset.is_valid():
            assessments = []

            # This is used to check for Assessment duplicates
            assessmentNames = []
            # This is used to check that the Assessmet weight sum is equal to 1 in the end
            weightSum = 0
            for form in assessment_formset:
                weight = form.cleaned_data.get('weight')
                weightSum += weight
                name = form.cleaned_data.get('assessmentName')
                marks = form.cleaned_data.get('totalMarks')
                dueDate = form.cleaned_data.get('dueDate')
                componentNumberNeeded = form.cleaned_data.get('componentNumberNeeded')
                slug = slugify(name)

                # Check if Assessment has already been added
                try:
                    assessment = Assessment.objects.get(course=course, assessmentName=name)
                    messages.error(request, 'Assessment ' + '"' + str(name) + '"' + ' has already been added!')
                    return redirect(reverse('chemapp:add_assessments', kwargs={'course_name_slug': course_name_slug}))
                except Assessment.DoesNotExist:
                    pass

                # Check for duplicates
                if name in assessmentNames:
                    messages.error(request, "Duplicate Assessment " + name)
                    return redirect(reverse('chemapp:add_assessments', kwargs={'course_name_slug': course_name_slug}))
                else:
                    assessmentNames.append(name)
                    assessments.append(Assessment(weight=weight,
                                                  assessmentName=name,
                                                  totalMarks=marks,
                                                  dueDate=dueDate,
                                                  componentNumberNeeded=componentNumberNeeded,
                                                  course=course,
                                                  slug=slug))

            # Check that the weights add to 1
            if weightSum != 1:
                messages.error(request, 'The sum of the Assessment Weights must be equal to 1')
                return redirect(reverse('chemapp:add_assessments', kwargs={'course_name_slug': course_name_slug}))
            else:
                Assessment.objects.bulk_create(assessments)
                assessmentsCreated = Assessment.objects.filter(course=course)

                assessment_name_slug = assessmentsCreated.first().slug
                return redirect(reverse('chemapp:add_assessmentComponents',
                                        kwargs={'course_name_slug': course_name_slug,
                                                'assessment_name_slug': assessment_name_slug}))
        else:
            print(assessment_formset.errors)
    else:
        assessment_formset = AssessmentFormSet()

    addAssessmentsDict['assessment_formset'] = assessment_formset

    return render(request, 'chemapp/add_assessments.html', context=addAssessmentsDict)


@login_required
def add_assessmentComponents(request, course_name_slug, assessment_name_slug):
    AssessmentComponentFormSet = formset_factory(AssessmentComponentForm, extra=1)
    course = Course.objects.get(slug=course_name_slug)
    allAssessments = Assessment.objects.filter(course=course)
    assessment = Assessment.objects.get(course=course, slug=assessment_name_slug)

    addAssessmentComponentsDict = {}
    addAssessmentComponentsDict['course_name_slug'] = course_name_slug
    addAssessmentComponentsDict['assessment_name_slug'] = assessment_name_slug
    addAssessmentComponentsDict['assessment'] = assessment.assessmentName

    if (request.method == 'POST'):
        assessmentComponent_formset = AssessmentComponentFormSet(request.POST)

        if assessmentComponent_formset.is_valid():
            assessmentComponents = []

            # This is used to check for Component duplicates
            componentDescriptions = []
            for form in assessmentComponent_formset:
                required = form.cleaned_data.get('required')
                marks = form.cleaned_data.get('marks')
                description = form.cleaned_data.get('description')

                if required == True:
                    status = 'Required'
                else:
                    status = 'Optional'

                # Check if Assessment Component has already been added
                try:
                    component = AssessmentComponent.objects.get(assessment=assessment, description=description)
                    messages.error(request,
                                   'Assessment Component ' + '"' + str(description) + '"' + ' has already been added!')
                    return redirect(reverse('chemapp:add_assessmentComponents',
                                            kwargs={'course_name_slug': course_name_slug,
                                                    'assessment_name_slug': assessment_name_slug}))
                except AssessmentComponent.DoesNotExist:
                    pass

                # Check for duplicates
                if description in componentDescriptions:
                    messages.error(request, "Duplicate Assessment Component " + description)
                    return redirect(reverse('chemapp:add_assessmentComponents',
                                            kwargs={'course_name_slug': course_name_slug,
                                                    'assessment_name_slug': assessment_name_slug}))
                else:
                    componentDescriptions.append(description)
                    assessmentComponents.append(AssessmentComponent(required=required,
                                                                    status=status,
                                                                    marks=marks,
                                                                    description=description,
                                                                    assessment=assessment))

            AssessmentComponent.objects.bulk_create(assessmentComponents)
            assessment.componentsAdded = True
            assessment.save()

            for assessment in allAssessments:
                if assessment.componentsAdded == False:
                    assessment_name_slug = assessment.slug
                    return redirect(reverse('chemapp:add_assessmentComponents',
                                            kwargs={'course_name_slug': course_name_slug,
                                                    'assessment_name_slug': assessment_name_slug}))

            # Success message
            messages.success(request,
                             "Added a course along with its corresponding assessments and components successfully")
            return redirect(reverse('chemapp:courses'))

        else:
            print(assessmentComponent_formset.errors)
    else:
        assessmentComponent_formset = AssessmentComponentFormSet()

    addAssessmentComponentsDict['assessmentComponent_formset'] = assessmentComponent_formset

    return render(request, 'chemapp/add_assessmentComponents.html', context=addAssessmentComponentsDict)


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
    studentsDict = {}
    # checking order by
    students = Student.objects.order_by('level')
    studentsDict['students'] = students

    return render(request, 'chemapp/students.html', context=studentsDict)


# Dictionary structure
# studentDict = {'student':studentObject,
#                'courses':{courseObject1:{'gradeObject':courseGradeObject,
#                                          'assessmentList':[{assessmentObject:{'gradeObject':assessmentGradeObject,
#                                                                               'componentList':[{componentObject:grade},{componentObject:grade}]}},
#                                                            {assessmentObject:{'gradeObject':assessmentGradeObject,
#                                                                                'componentList':[{componentObject:grade},{componentObject:grade}]}},
#                                                           ]},
#                           courseObject2:{'gradeObject':courseGradeObject,
#                                          'assessmentList':[{assessmentObject:{'gradeObject':assessmentGradeObject,
#                                                                              'componentList':[{componentObject:grade},{componentObject:grade}]}},
#                                                            {assessmentObject:{'gradeObject':assessmentGradeObject,
#                                                                                'componentList':[{componentObject:grade},{componentObject:grade}]}},
#                                                           ]},
@login_required
def student(request, student_id):
    studentDict = {}
    try:
        student = Student.objects.get(studentID=student_id)
        studentDict['student'] = student
        studentDict['courses'] = {}
        studentDict['student_id'] = student_id

        for course in student.courses.all():
            studentDict['courses'][course] = {}

            try:
                courseGrade = CourseGrade.objects.get(course=course, student=student)
                studentDict['courses'][course]['gradeObject'] = courseGrade

            except CourseGrade.DoesNotExist:
                studentDict['courses'][course]['gradeObject'] = None

            studentDict['courses'][course]['assessmentList'] = []

            assessments = Assessment.objects.filter(course=course)

            for assessment in assessments:
                assessmentDict = {}
                assessmentDict[assessment] = {}

                try:
                    assessmentGrade = AssessmentGrade.objects.get(assessment=assessment, student=student)
                    assessmentDict[assessment]['gradeObject'] = assessmentGrade

                except AssessmentGrade.DoesNotExist:
                    assessmentDict[assessment]['gradeObject'] = None

                assessmentDict[assessment]['componentList'] = []

                components = AssessmentComponent.objects.filter(assessment=assessment)

                for component in components:
                    componentDict = {}
                    try:
                        assessmentComponentGrade = AssessmentComponentGrade.objects.get(assessmentComponent=component,
                                                                                        student=student)
                        grade = assessmentComponentGrade.grade
                    except AssessmentComponentGrade.DoesNotExist:
                        grade = None

                    componentDict[component] = grade
                    assessmentDict[assessment]['componentList'].append(componentDict)

                studentDict['courses'][course]['assessmentList'].append(assessmentDict)

    except Student.DoesNotExist:
        raise Http404("Student does not exist")

    return render(request, 'chemapp/student.html', context=studentDict)


@login_required
def add_student(request):
    addStudentDict = {}

    if request.method == 'POST':
        student_form = StudentForm(request.POST)
        if student_form.is_valid():
            student = student_form.save(commit=False)

            gapYear = student_form.cleaned_data.get('gapYear')
            if gapYear == False:
                status = 'Enrolled'
            else:
                status = 'Gap Year'

            student.status = status
            # Just to test until we have correct equation && 000000 did not allow for more students since it has to be unique
            student.anonID = random.randint(0, 99999)
            student.save()

            # Populate student's courses
            degree = student.academicPlan
            student.courses.set(Course.objects.filter(degree=degree, level=student.level))
            student.save()

            # Increment each course student count
            courses = Course.objects.filter(degree=degree, level=student.level)
            for course in courses:
                course.numberOfStudents = course.numberOfStudents + 1
                course.save()

            # Increment degree student count
            degree.numberOfStudents = degree.numberOfStudents + 1
            degree.save()

            # Success message
            messages.success(request, "Student Added Successfully")
            return redirect(reverse('chemapp:students'))

        else:
            print(student_form.errors)
    else:
        student_form = StudentForm()

    addStudentDict['student_form'] = student_form
    return render(request, 'chemapp/add_student.html', context=addStudentDict)


@login_required
def add_grades(request, student_id, course_name_slug, assessment_name_slug):
    student = Student.objects.get(studentID=student_id)
    course = Course.objects.get(slug=course_name_slug)
    assessment = Assessment.objects.get(course=course, slug=assessment_name_slug)
    components = AssessmentComponent.objects.filter(assessment=assessment)

    addGradeDict = {}
    addGradeDict['assessment'] = assessment
    addGradeDict['components'] = components
    addGradeDict['student_id'] = student_id
    addGradeDict['course_name_slug'] = course_name_slug
    addGradeDict['assessment_name_slug'] = assessment_name_slug

    ComponentGradeFormSet = formset_factory(AssessmentComponentGradeForm, extra=0)

    if (request.method == 'POST'):
        component_grade_formset = ComponentGradeFormSet(request.POST)
        assessment_grade_form = AssessmentGradeForm(request.POST)

        if assessment_grade_form.is_valid() and component_grade_formset.is_valid():
            grades = []
            for form in component_grade_formset:
                grade = form.cleaned_data.get('grade')
                assessmentComponent = form.cleaned_data.get('assessmentComponent')

                grades.append(AssessmentComponentGrade(grade=grade,
                                                       assessmentComponent=assessmentComponent,
                                                       student=student))

                # Check if Grades have already been added
                try:
                    assessmentComponentGrade = AssessmentComponentGrade.objects.get(
                        assessmentComponent=assessmentComponent, student=student)
                    messages.error(request, 'Grade for ' + str(assessmentComponent.description) + ' already added!')
                    return redirect(reverse('chemapp:add_grades', kwargs={'student_id': student_id,
                                                                          'course_name_slug': course_name_slug,
                                                                          'assessment_name_slug': assessment_name_slug}))

                except AssessmentComponentGrade.DoesNotExist:
                    pass

                # Check if required grade is added
                if assessmentComponent.required == True and grade is None:
                    messages.error(request, 'Grade for ' + str(assessmentComponent.description) + ' is required!')
                    return redirect(reverse('chemapp:add_grades', kwargs={'student_id': student_id,
                                                                          'course_name_slug': course_name_slug,
                                                                          'assessment_name_slug': assessment_name_slug}))
                else:
                    pass

                # Check if supplied grade is more than the available marks
                if grade is not None and grade > assessmentComponent.marks:
                    messages.error(request,
                                   'Grade for ' + str(assessmentComponent.description) + ' exceeds available marks!')
                    return redirect(reverse('chemapp:add_grades', kwargs={'student_id': student_id,
                                                                          'course_name_slug': course_name_slug,
                                                                          'assessment_name_slug': assessment_name_slug}))
                else:
                    pass

            AssessmentComponentGrade.objects.bulk_create(grades)

            # Creating assessmentGrade object
            # Calculating marked grade
            count = 0
            grade = 0
            for component in components:
                assessmentComponentGrade = AssessmentComponentGrade.objects.get(assessmentComponent=component)
                if assessmentComponentGrade.grade is not None:
                    count = count + 1
                    grade = grade + assessmentComponentGrade.grade

            submissionDate = assessment_grade_form.cleaned_data.get('submissionDate')
            noDetriment = assessment_grade_form.cleaned_data.get('noDetriment')
            goodCause = assessment_grade_form.cleaned_data.get('goodCause')

            # Check if submission date and time is after due date
            if submissionDate > assessment.dueDate:
                late = True
            else:
                late = False

            # Check if the number of components answered match number of components needed
            if count == assessment.componentNumberNeeded:
                componentNumberMatch = True
            else:
                componentNumberMatch = False

            AssessmentGrade.objects.create(submissionDate=submissionDate,
                                           noDetriment=noDetriment,
                                           goodCause=goodCause,
                                           markedGrade=grade,
                                           finalGrade=None,
                                           finalGrade22Scale=None,
                                           band=None,
                                           componentNumberAnswered=count,
                                           componentNumberMatch=componentNumberMatch,
                                           late=late,
                                           assessment=assessment,
                                           student=student)

            # Success message
            messages.success(request, 'Grades Added Successfully')
            return redirect(reverse('chemapp:student', kwargs={'student_id': student_id, }))

        else:
            print(assessment_grade_form, component_grade_formset.errors)
    else:
        component_grade_formset = ComponentGradeFormSet(initial=[{'assessmentComponent': component,
                                                                  'description': str(
                                                                      component.description) + ' (' + str(
                                                                      component.marks) + ')' + ' ' + str(
                                                                      component.status)}
                                                                 for component in components])
        assessment_grade_form = AssessmentGradeForm()

    addGradeDict['component_grade_formset'] = component_grade_formset
    addGradeDict['assessment_grade_form'] = assessment_grade_form

    return render(request, 'chemapp/add_grades.html', context=addGradeDict)


@login_required
def add_final_grade(request, student_id, course_name_slug, assessment_name_slug):
    student = Student.objects.get(studentID=student_id)
    course = Course.objects.get(slug=course_name_slug)
    assessment = Assessment.objects.get(course=course, slug=assessment_name_slug)
    assessmentGrade = AssessmentGrade.objects.get(assessment=assessment, student=student)

    addfinalGradeDict = {}
    addfinalGradeDict['assessment'] = assessment
    addfinalGradeDict['assessmentGrade'] = assessmentGrade
    addfinalGradeDict['student_id'] = student_id
    addfinalGradeDict['course_name_slug'] = course_name_slug
    addfinalGradeDict['assessment_name_slug'] = assessment_name_slug

    if (request.method == 'POST'):
        final_grade_form = FinalAssessmentGradeForm(request.POST)

        if final_grade_form.is_valid():
            finalGrade = final_grade_form.cleaned_data.get('finalGrade')
            finalGrade22Scale = round((finalGrade * 22) / assessmentGrade.assessment.totalMarks)
            band = GRADE_TO_BAND[finalGrade22Scale]

            assessmentGrade.finalGrade = finalGrade
            assessmentGrade.finalGrade22Scale = finalGrade22Scale
            assessmentGrade.band = band
            assessmentGrade.save()

            # Check if Course Grade can be calculated
            canCourseGradeBeCalculated = True
            assessments = Assessment.objects.filter(course=course)
            assessmentGrades = []
            for assessment in assessments:
                try:
                    assessmentGradeObject = AssessmentGrade.objects.get(assessment=assessment, student=student)

                    if (assessmentGradeObject.finalGrade is None):
                        canCourseGradeBeCalculated = False
                    else:
                        assessmentGrades.append(assessmentGradeObject)

                except AssessmentGrade.DoesNotExist:
                    canCourseGradeBeCalculated = False

            if canCourseGradeBeCalculated == False:
                # Success message
                # Final assessment grade added but course grade cannot be calculated
                messages.success(request, 'Final Grade Added Successfully')
                return redirect(reverse('chemapp:student', kwargs={'student_id': student_id, }))
            else:
                courseGrade = 0
                for assessmentGrade in assessmentGrades:
                    weight = assessmentGrade.assessment.weight
                    weightedGrade = weight * assessmentGrade.finalGrade22Scale
                    courseGrade = courseGrade + weightedGrade

                courseGrade = round(courseGrade)
                band = GRADE_TO_BAND[courseGrade]

                courseGradeObject = CourseGrade.objects.create(course=course, student=student,   band=band)

                # Success message
                # Final assessment grade added and course grade calculated
                messages.success(request, 'Final Grade Added Successfully and Course Grade Calculated!')
                return redirect(reverse('chemapp:student', kwargs={'student_id': student_id, }))

        else:
            print(final_grade_form.errors)

    else:
        final_grade_form = FinalAssessmentGradeForm()

    addfinalGradeDict['final_grade_form'] = final_grade_form
    return render(request, 'chemapp/add_final_grade.html', context=addfinalGradeDict)


@login_required
def upload_student_csv(request):
    # student_dict = {'boldmessage':'Upload csv file to add students'}
    # return render(request,'chemapp/upload_student_csv.html', context=student_dict)
    template = 'chemapp/upload_student_csv.html'
    data = Student.objects.all()

    prompt = {'Order': 'studentID,firstName,lastName,academicPlan,anonID,currentYear', 'students': data}
    if request.method == "GET":
        return render(request, template, prompt)

    csv_file = request.FILES['file']
    if not csv_file.name.endswith('.csv'):
        messages.error(request, 'THIS IS NOT A CSV FILE')

    data_set = csv_file.read().decode('UTF-8')
    io_string = io.StringIO(data_set)
    next(io_string)
    for column in csv.reader(io_string, delimiter=',', quotechar="|"):
        if not Student.objects.filter(studentID=column[0]).exists():
            degree = Degree.objects.get(degreeCode=column[3])
            degree.numberOfStudents = degree.numberOfStudents + 1
            degree.save()
        _, created = Student.objects.update_or_create(
            studentID=column[0],
            firstName=column[1],
            lastName=column[2],
            academicPlan=Degree.objects.get(degreeCode=column[3]),
            level=column[4],
            anonID=column[5],
            graduationDate=column[6],
        )

    context = {}
    messages.success(request, "Student Added Successfully")
    return redirect(reverse('chemapp:students'))


@login_required
def upload_degree_csv(request):
    template = 'chemapp/upload_degree_csv.html'
    data = Degree.objects.all()

    if request.method == "GET":
        return render(request, template)

    csv_file = request.FILES['file']
    if not csv_file.name.endswith('.csv'):
        messages.error(request, 'THIS IS NOT A CSV FILE')

    data_set = csv_file.read().decode('UTF-8')
    io_string = io.StringIO(data_set)
    next(io_string)
    for column in csv.reader(io_string, delimiter=',', quotechar="|"):
        _, created = Degree.objects.update_or_create(
            degreeCode=column[0],
        )
    context = {}
    messages.success(request, "Degrees Added Successfully")
    return redirect(reverse('chemapp:degrees'))


@login_required
def upload_course_csv(request):
    template = 'chemapp/upload_course_csv.html'
    data = Course.objects.all()

    if request.method == "GET":
        return render(request, template)

    csv_file = request.FILES['file']
    if not csv_file.name.endswith('.csv'):
        messages.error(request, 'THIS IS NOT A CSV FILE')

    data_set = csv_file.read().decode('UTF-8')
    io_string = io.StringIO(data_set)
    next(io_string)
    for column in csv.reader(io_string, delimiter=',', quotechar="|"):
        if not Course.objects.filter(code=column[0]).exists():
            degree = Degree.objects.get(degreeCode=column[1])
            degree.numberOfCourses = degree.numberOfCourses + 1
            degree.save()
        _, created = Course.objects.update_or_create(
            code=column[0],
            degree=Degree.objects.get(degreeCode=column[1]),
            creditsWorth=column[2],
            name=column[3],
            shortHand=column[4],
            level=column[5],
            year=column[6],
            academicYearTaught=column[7],
            semester=column[8],
            minimumPassGrade=column[9],
            minimumRequirementsForCredit=column[10],
            description=column[11],
            comments=column[12],

        )
    context = {}
    messages.success(request, "Courses Added Successfully")
    return redirect(reverse('chemapp:courses'))


@login_required
def upload_assessment_csv(request, course_code):
    template = 'chemapp/upload_assessment_csv.html'
    data = Assessment.objects.all()
    weightsum = 0

    if request.method == "GET":
        return render(request, template)

    csv_file = request.FILES['file']
    if not csv_file.name.endswith('.csv'):
        messages.error(request, 'THIS IS NOT A CSV FILE')

    data_set = csv_file.read().decode('UTF-8')
    io_string = io.StringIO(data_set)
    next(io_string)
    for column in csv.reader(io_string, delimiter=',', quotechar="|"):
        weightsum = weightsum + int(column[2])
        _, created = Assessment.objects.update_or_create(
            weight=column[2],
            totalMarks=column[1],
            assessmentName=column[0],
            dueDate=column[3],
            course=Course.objects.get(code=course_code),
            componentNumberNeeded=column[4],
        )
    if weightsum != 1:
        messages.error(request, 'The sum of the Assessment Weights must be equal to 1')
        return redirect(reverse('chemapp:courses'))

    else:
        messages.success(request, "Assessment Added Successfully")
        return redirect(reverse('chemapp:courses'))
