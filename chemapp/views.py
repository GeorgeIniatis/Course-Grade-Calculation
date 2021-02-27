from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from chemapp.models import *
from chemapp.forms import *
import csv, io
from django.forms.formsets import formset_factory
from django.template.defaultfilters import slugify
from django.db.models import Q
import random
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from chemapp.utils import user_edit_perm_check, permission_required_context, user_upload_grades_perm_check
from django.contrib.auth.decorators import permission_required
from datetime import datetime
import pytz

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
    context_dict = {'boldmessage': 'Home'}
    return render(request, 'chemapp/home.html', context=context_dict)


@login_required
def about(request):
    context_dict = {'boldmessage': 'About'}
    return render(request, 'chemapp/about.html', context=context_dict)


@login_required
def degrees(request):
    degreesDict = {}

    degrees = Degree.objects.all()
    degreesDict['degrees'] = degrees

    return render(request, 'chemapp/degrees.html', context=degreesDict)


@login_required
@permission_required_context('chemapp.add_degree', 'No permission to add_degree', raise_exception=True)
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
                slug = slugify(degreeCode)

                if degreeCode in codes:
                    messages.error(request, "Duplicate degree " + degreeCode + " was only added once")
                else:
                    codes.append(degreeCode)
                    degrees.append(Degree(degreeCode=degreeCode,
                                          name=name,
                                          slug=slug,
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
@permission_required_context('chemapp.change_degree', 'No permission to edit_degree', raise_exception=True)
def edit_degree(request, degree_code_slug):
    degree = Degree.objects.get(slug=degree_code_slug)

    editDegreeDict = {}
    editDegreeDict['degree_code_slug'] = degree_code_slug
    editDegreeDict['degree'] = degree

    if (request.method == 'POST'):
        edit_degree_form = EditDegreeForm(request.POST)

        if edit_degree_form.is_valid():
            name = edit_degree_form.cleaned_data.get('name')

            degree.name = name

            degree.save()

            messages.success(request, 'Degree was updated successfully!')
            return redirect(reverse('chemapp:degrees'))
        else:
            print(edit_degree_form.errors)
    else:
        edit_degree_form = EditDegreeForm(instance=degree)

    editDegreeDict['edit_degree_form'] = edit_degree_form

    return render(request, 'chemapp/edit_degree.html', context=editDegreeDict)


@login_required
@permission_required_context('chemapp.delete_degree', 'No permission to delete_degree', raise_exception=True)
def delete_degree(request, degree_code_slug):
    degree = Degree.objects.get(slug=degree_code_slug)

    if request.method == 'POST':
        degree.delete()

        messages.success(request, 'Degree deleted successfully!')
        return redirect(reverse('chemapp:degrees'))

    return render(request, 'chemapp/degrees.html', context={})


@login_required
def courses(request):
    coursesDict = {}
    courses = Course.objects.all()

    yearDict = {}

    for course in courses:
        year = course.year
        slug = course.slug
        code = course.code
        color = course.courseColor
        level = course.level
        name = course.name

        if year not in yearDict.values():
            yearDict[year] = year

        courseList = [year, slug, code, color, level,name]

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
    courseDict['course_name_slug'] = course_name_slug

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
def course_students(request, course_name_slug):
    courseStudentsDict = {}
    courseStudentsDict['course_name_slug'] = course_name_slug
    course = Course.objects.get(slug=course_name_slug)
    students = Student.objects.filter(courses=course)
    courseStudentsDict['students'] = students

    return render(request, 'chemapp/course_students.html', context=courseStudentsDict)


@login_required
@permission_required_context('chemapp.add_course', 'No permission to add_course', raise_exception=True)
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

            content_type = ContentType.objects.get_for_model(Course)
            Permission.objects.create(codename='can_edit_course' + course_slug, name="can edit course " + course_slug,
                                      content_type=content_type, )
            Permission.objects.create(codename='can_upload_grades_for' + course_slug,
                                      name="can upload grades for " + course_slug, content_type=content_type, )

            # Increment degree course count
            degree = course.degree
            degree.numberOfCourses = degree.numberOfCourses + 1
            degree.save()

            # Success message
            messages.success(request, "Course added successfully!")
            return redirect(reverse('chemapp:add_lecturers', kwargs={'course_name_slug': course_slug}))

        else:
            messages.error(request, 'Course has already been added!')
            print(course_form.errors)
    else:
        course_form = CourseForm()

    addCourseDict['course_form'] = CourseForm()

    return render(request, 'chemapp/add_course.html', context=addCourseDict)


@login_required
def add_lecturers(request, course_name_slug):
    CourseLecturerDict = {}
    CourseLecturerDict['course_name_slug'] = course_name_slug
    CourseLecturerDict['lecturers'] = Staff.objects.all()
    course = Course.objects.get(slug=course_name_slug)

    if (request.method == 'POST'):
        lect = request.POST.getlist('lecturers_list')
        lecturers_list = []
        for lecture in lect:
            lecturers_list.append(Staff.objects.get(staffID=lecture))
        course.lecturers.add(*lecturers_list)
        messages.success(request, 'Course was updated successfully!')
        return redirect(reverse('chemapp:add_assessments', kwargs={'course_name_slug': course_name_slug}))
    else:
        course_lecturer_form = CourseLecturerForm(instance=course)

    CourseLecturerDict['course_lecturer_form'] = course_lecturer_form

    return render(request, 'chemapp/add_lecturers.html', context=CourseLecturerDict)


@login_required
@user_edit_perm_check
def edit_course(request, course_name_slug):
    editCourseDict = {}
    editCourseDict['course_name_slug'] = course_name_slug
    course = Course.objects.get(slug=course_name_slug)

    if (request.method == 'POST'):
        edit_course_form = EditCourseForm(request.POST)

        if edit_course_form.is_valid():
            name = edit_course_form.cleaned_data.get('name')
            shortHand = edit_course_form.cleaned_data.get('shortHand')
            creditsWorth = edit_course_form.cleaned_data.get('creditsWorth')
            level = edit_course_form.cleaned_data.get('level')
            academicYearTaught = edit_course_form.cleaned_data.get('academicYearTaught')
            semester = edit_course_form.cleaned_data.get('semester')
            minimumPassGrade = edit_course_form.cleaned_data.get('minimumPassGrade')
            minimumRequirementsForCredit = edit_course_form.cleaned_data.get('minimumRequirementsForCredit')
            description = edit_course_form.cleaned_data.get('description')
            comments = edit_course_form.cleaned_data.get('comments')
            courseColor = edit_course_form.cleaned_data.get('courseColor')

            course.name = name
            course.shortHand = shortHand
            course.creditsWorth = creditsWorth
            course.level = level
            course.academicYearTaught = academicYearTaught
            course.semester = semester
            course.minimumPassGrade = minimumPassGrade
            course.minimumRequirementsForCredit = minimumRequirementsForCredit
            course.description = description
            course.comments = comments
            course.courseColor = courseColor

            course.save()

            messages.success(request, 'Course was updated successfully!')
            return redirect(reverse('chemapp:course', kwargs={'course_name_slug': course_name_slug}))
        else:
            print(edit_course_form.errors)
    else:
        edit_course_form = EditCourseForm(instance=course)

    editCourseDict['edit_course_form'] = edit_course_form

    return render(request, 'chemapp/edit_course.html', context=editCourseDict)


@login_required
def delete_course(request, course_name_slug):
    course = Course.objects.get(slug=course_name_slug)
    degree = course.degree

    if request.method == 'POST':
        course.delete()

        # Reduce degree course count
        degree.numberOfCourses = degree.numberOfCourses - 1
        degree.save()

        messages.success(request, 'Course deleted successfully!')
        return redirect(reverse('chemapp:courses'))

    return render(request, 'chemapp/course.html', context={})


@login_required
@permission_required_context('chemapp.add_assessments', 'No permission to add_assessments', raise_exception=True)
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

                # Success message
                messages.success(request, "Assessments added successfully!")
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
def edit_assessment(request, course_name_slug, assessment_name_slug):
    course = Course.objects.get(slug=course_name_slug)
    assessment = Assessment.objects.get(course=course, slug=assessment_name_slug)

    editAssessmentDict = {}
    editAssessmentDict['course_name_slug'] = course_name_slug
    editAssessmentDict['assessment_name_slug'] = assessment_name_slug
    editAssessmentDict['assessment'] = assessment

    if (request.method == 'POST'):
        edit_assessment_form = EditAssessmentForm(request.POST)

        if edit_assessment_form.is_valid():
            marks = edit_assessment_form.cleaned_data.get('totalMarks')
            dueDate = edit_assessment_form.cleaned_data.get('dueDate')
            componentNumberNeeded = edit_assessment_form.cleaned_data.get('componentNumberNeeded')

            assessment.totalMarks = marks
            assessment.dueDate = dueDate
            assessment.componentNumberNeeded = componentNumberNeeded

            assessment.save()

            messages.success(request, 'Assessment was updated successfully!')
            return redirect(reverse('chemapp:course', kwargs={'course_name_slug': course_name_slug}))
        else:
            print(edit_assessment_form.errors)
    else:
        edit_assessment_form = EditAssessmentForm(instance=assessment)

    editAssessmentDict['edit_assessment_form'] = edit_assessment_form

    return render(request, 'chemapp/edit_assessment.html', context=editAssessmentDict)


@login_required
def delete_assessment(request, course_name_slug, assessment_name_slug):
    course = Course.objects.get(slug=course_name_slug)
    assessment = Assessment.objects.get(course=course, slug=assessment_name_slug)

    if request.method == 'POST':
        assessment.delete()

        messages.success(request, 'Assessment deleted successfully!')
        return redirect(reverse('chemapp:course', kwargs={'course_name_slug': course_name_slug}))

    return render(request, 'chemapp/course.html', context={})


@login_required
@permission_required_context('chemapp.add_assessmentComponents', 'No permission to add_assessmentComponents',
                             raise_exception=True)
def add_assessmentComponents(request, course_name_slug, assessment_name_slug):
    AssessmentComponentFormSet = formset_factory(AssessmentComponentForm, extra=1)
    course = Course.objects.get(slug=course_name_slug)
    allAssessments = Assessment.objects.filter(course=course)
    assessment = Assessment.objects.get(course=course, slug=assessment_name_slug)

    addAssessmentComponentsDict = {}
    addAssessmentComponentsDict['course_name_slug'] = course_name_slug
    addAssessmentComponentsDict['assessment_name_slug'] = assessment_name_slug
    addAssessmentComponentsDict['assessment'] = assessment

    if (request.method == 'POST'):
        assessmentComponent_formset = AssessmentComponentFormSet(request.POST)

        if assessmentComponent_formset.is_valid():
            assessmentComponents = []

            # This is used to check for Component duplicates
            componentDescriptions = []
            for form in assessmentComponent_formset:
                required = form.cleaned_data.get('required')
                lecturer = form.cleaned_data.get('lecturers')
                marks = form.cleaned_data.get('marks')
                description = form.cleaned_data.get('description')
                slug = slugify(description)

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
                                                                    slug=slug,
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
            messages.success(request, "Components added successfully!")
            return redirect(reverse('chemapp:course', kwargs={'course_name_slug': course_name_slug}))

        else:
            print(assessmentComponent_formset.errors)
    else:
        assessmentComponent_formset = AssessmentComponentFormSet()

    addAssessmentComponentsDict['assessmentComponent_formset'] = assessmentComponent_formset

    return render(request, 'chemapp/add_assessmentComponents.html', context=addAssessmentComponentsDict)


@login_required
def edit_assessmentComponent(request, course_name_slug, assessment_name_slug, assessment_component_slug):
    course = Course.objects.get(slug=course_name_slug)
    assessment = Assessment.objects.get(course=course, slug=assessment_name_slug)
    component = AssessmentComponent.objects.get(assessment=assessment, slug=assessment_component_slug)

    editComponentDict = {}
    editComponentDict['course_name_slug'] = course_name_slug
    editComponentDict['assessment_name_slug'] = assessment_name_slug
    editComponentDict['assessment_component_slug'] = assessment_component_slug
    editComponentDict['component'] = component

    if (request.method == 'POST'):
        edit_component_form = EditAssessmentComponentForm(request.POST)

        if edit_component_form.is_valid():
            required = edit_component_form.cleaned_data.get('required')
            marks = edit_component_form.cleaned_data.get('marks')

            component.required = required
            component.marks = marks

            component.save()

            messages.success(request, 'Assessment Component was updated successfully!')
            return redirect(reverse('chemapp:course', kwargs={'course_name_slug': course_name_slug}))
        else:
            print(edit_component_form.errors)
    else:
        edit_component_form = EditAssessmentComponentForm(instance=component)

    editComponentDict['edit_component_form'] = edit_component_form

    return render(request, 'chemapp/edit_component.html', context=editComponentDict)


@login_required
def delete_assessmentComponent(request, course_name_slug, assessment_name_slug, assessment_component_slug):
    course = Course.objects.get(slug=course_name_slug)
    assessment = Assessment.objects.get(course=course, slug=assessment_name_slug)
    component = AssessmentComponent.objects.get(assessment=assessment, slug=assessment_component_slug)

    if request.method == 'POST':
        component.delete()

        messages.success(request, 'Assessment Component deleted successfully!')
        return redirect(reverse('chemapp:course', kwargs={'course_name_slug': course_name_slug}))

    return render(request, 'chemapp/course.html', context={})


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
@permission_required_context('chemapp.add_student', 'No permission to add_student', raise_exception=True)
def add_student(request):
    addStudentDict = {}

    if request.method == 'POST':
        student_form = StudentForm(request.POST)
        if student_form.is_valid():
            studentID = student_form.cleaned_data.get('studentID')
            firstName = student_form.cleaned_data.get('firstName')
            lastName = student_form.cleaned_data.get('lastName')
            gapYear = student_form.cleaned_data.get('gapYear')
            academicPlan = student_form.cleaned_data.get('academicPlan')
            level = student_form.cleaned_data.get('level')
            graduationDate = student_form.cleaned_data.get('graduationDate')
            comments = student_form.cleaned_data.get('comments')
            courses = student_form.cleaned_data.get('courses')

            if gapYear == False:
                status = 'Enrolled'
            else:
                status = 'Gap Year'

            anonID = (abs(hash(str(studentID)))) / studentID

            student = Student.objects.create(studentID=studentID, anonID=anonID, firstName=firstName, lastName=lastName,
                                             gapYear=gapYear, status=status, academicPlan=academicPlan, level=level,
                                             graduationDate=graduationDate,
                                             comments=comments)

            # Populate student's courses
            student.courses.set(courses)
            student.save()

            # Increment degree student count
            degree = student.academicPlan
            degree.numberOfStudents = degree.numberOfStudents + 1
            degree.save()

            # Increment each course student count
            courses = student.courses.all()
            for course in courses:
                course.numberOfStudents = course.numberOfStudents + 1
                course.save()

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
def edit_student(request, student_id):
    student = Student.objects.get(studentID=student_id)

    editStudentDict = {}
    editStudentDict['student_id'] = student_id
    editStudentDict['student'] = student

    if (request.method == 'POST'):
        edit_student_form = EditStudentForm(request.POST)

        if edit_student_form.is_valid():
            # Reduce degree student count
            degree = student.academicPlan
            degree.numberOfStudents = degree.numberOfStudents - 1
            degree.save()

            firstName = edit_student_form.cleaned_data.get('firstName')
            lastName = edit_student_form.cleaned_data.get('lastName')
            gapYear = edit_student_form.cleaned_data.get('gapYear')
            academicPlan = edit_student_form.cleaned_data.get('academicPlan')
            level = edit_student_form.cleaned_data.get('level')
            graduationDate = edit_student_form.cleaned_data.get('graduationDate')
            comments = edit_student_form.cleaned_data.get('comments')
            courses = edit_student_form.cleaned_data.get('courses')

            # These two for loops are to prevent having to reset all courses when updating
            # Course being removed
            for course in student.courses.all():
                if course not in courses:
                    # Reduce course student count
                    course.numberOfStudents = course.numberOfStudents - 1
                    course.save()
                    # Remove course association with student
                    student.courses.remove(course)

            # Course being added
            for course in courses:
                if course not in student.courses.all():
                    # Increase course student count
                    course.numberOfStudents = course.numberOfStudents + 1
                    course.save()
                    # Associate course with student
                    student.courses.add(course)

            student.firstName = firstName
            student.lastName = lastName
            student.gapYear = gapYear
            student.academicPlan = academicPlan
            student.level = level
            student.graduationDate = graduationDate
            student.comments = comments

            student.save()

            student = Student.objects.get(studentID=student_id)
            # Increment degree student count
            degree = student.academicPlan
            degree.numberOfStudents = degree.numberOfStudents + 1
            degree.save()

            messages.success(request, 'Student was updated successfully!')
            return redirect(reverse('chemapp:student', kwargs={'student_id': student_id}))
        else:
            print(edit_student_form.errors)
    else:
        edit_student_form = EditStudentForm(instance=student)

    editStudentDict['edit_student_form'] = edit_student_form

    return render(request, 'chemapp/edit_student.html', context=editStudentDict)


@login_required
def delete_student(request, student_id):
    student = Student.objects.get(studentID=student_id)
    degree = student.academicPlan
    courses = student.courses.all()

    if request.method == 'POST':
        # Reduce degree student count
        degree.numberOfStudents = degree.numberOfStudents - 1
        degree.save()

        # Reduce each course student count
        for course in courses:
            course.numberOfStudents = course.numberOfStudents - 1
            course.save()

        student.delete()

        messages.success(request, 'Student deleted successfully!')
        return redirect(reverse('chemapp:students'))

    return render(request, 'chemapp/student.html', context={})


@login_required
def ajax_filter_courses(request):
    degree = request.GET.get('degree')
    courses = Course.objects.filter(degree=degree).order_by('year')
    return render(request, 'chemapp/courses_dropdown_list.html', {'courses': courses})


@login_required
@user_upload_grades_perm_check
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
def edit_grades(request, student_id, course_name_slug, assessment_name_slug):
    student = Student.objects.get(studentID=student_id)
    course = Course.objects.get(slug=course_name_slug)
    assessment = Assessment.objects.get(course=course, slug=assessment_name_slug)
    components = AssessmentComponent.objects.filter(assessment=assessment)

    assessmentGrade = AssessmentGrade.objects.get(assessment=assessment, student=student)

    editGradesDict = {}
    editGradesDict['assessment'] = assessment
    editGradesDict['components'] = components
    editGradesDict['student_id'] = student_id
    editGradesDict['course_name_slug'] = course_name_slug
    editGradesDict['assessment_name_slug'] = assessment_name_slug

    ComponentGradeFormSet = formset_factory(AssessmentComponentGradeForm, extra=0)

    if (request.method == 'POST'):
        component_grade_formset = ComponentGradeFormSet(request.POST)
        assessment_grade_form = AssessmentGradeForm(request.POST)

        if assessment_grade_form.is_valid() and component_grade_formset.is_valid():
            # Dictionary structure
            # grades = { assessmentComponent:grade,
            #            assessmentComponent2:grade2 }
            grades = {}
            for form in component_grade_formset:
                grade = form.cleaned_data.get('grade')
                assessmentComponent = form.cleaned_data.get('assessmentComponent')

                grades[assessmentComponent] = grade

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

            # Individually update grades
            for component, grade in grades.items():
                assessmentComponentGrade = AssessmentComponentGrade.objects.get(assessmentComponent=component,
                                                                                student=student)
                assessmentComponentGrade.grade = grade
                assessmentComponentGrade.save()

            # Updating assessmentGrade object
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

            # Update Assessment Grade
            assessmentGrade = AssessmentGrade.objects.get(assessment=assessment, student=student)

            assessmentGrade.submissionDate = submissionDate
            assessmentGrade.noDetriment = noDetriment
            assessmentGrade.goodCause = goodCause
            assessmentGrade.markedGrade = grade
            assessmentGrade.finalGrade = None
            assessmentGrade.finalGrade22Scale = None
            assessmentGrade.band = None
            assessmentGrade.componentNumberAnswered = count
            assessmentGrade.componentNumberMatch = componentNumberMatch
            assessmentGrade.late = late
            assessmentGrade.assessment = assessment
            assessmentGrade.student = student

            assessmentGrade.save()

            # Delete Course Grade if possible
            try:
                courseGrade = CourseGrade.objects.get(course=course, student=student)
                courseGrade.delete()
            except CourseGrade.DoesNotExist:
                pass

            # Success message
            messages.success(request, 'Grades Updated Successfully')
            return redirect(reverse('chemapp:student', kwargs={'student_id': student_id, }))

        else:
            print(assessment_grade_form, component_grade_formset.errors)
    else:
        component_grade_formset = ComponentGradeFormSet(initial=[{'assessmentComponent': component,
                                                                  'description': str(
                                                                      component.description) + ' (' + str(
                                                                      component.marks) + ')' + ' ' + str(
                                                                      component.status),
                                                                  'grade': AssessmentComponentGrade.objects.get(
                                                                      assessmentComponent=component,
                                                                      student=student).grade}
                                                                 for component in components]
                                                        )
        assessment_grade_form = AssessmentGradeForm(instance=assessmentGrade)

    editGradesDict['component_grade_formset'] = component_grade_formset
    editGradesDict['assessment_grade_form'] = assessment_grade_form

    return render(request, 'chemapp/edit_grades.html', context=editGradesDict)


@login_required
def delete_grades(request, student_id, course_name_slug, assessment_name_slug):
    student = Student.objects.get(studentID=student_id)
    course = Course.objects.get(slug=course_name_slug)
    assessment = Assessment.objects.get(course=course, slug=assessment_name_slug)
    components = AssessmentComponent.objects.filter(assessment=assessment)

    if request.method == 'POST':
        # Delete Assessment Component Grades
        for component in components:
            assessmentComponentGrade = AssessmentComponentGrade.objects.get(assessmentComponent=component,
                                                                            student=student)
            assessmentComponentGrade.delete()

        # Delete Assessment Grade
        assessmentGrade = AssessmentGrade.objects.get(assessment=assessment, student=student)
        assessmentGrade.delete()

        # Delete Course Grade if possible
        try:
            courseGrade = CourseGrade.objects.get(course=course, student=student)
            courseGrade.delete()
        except CourseGrade.DoesNotExist:
            pass

        messages.success(request, 'Grades deleted successfully!')
        return redirect(reverse('chemapp:student', kwargs={'student_id': student_id, }))

    return render(request, 'chemapp/student.html', context={})


@login_required
@user_edit_perm_check
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

                courseGradeObject = CourseGrade.objects.create(course=course, student=student, grade=courseGrade,
                                                               band=band)

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
def edit_final_grade(request, student_id, course_name_slug, assessment_name_slug):
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

            # Delete Course Grade if possible in order to update later
            try:
                courseGrade = CourseGrade.objects.get(course=course, student=student)
                courseGrade.delete()
            except CourseGrade.DoesNotExist:
                pass

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
                # Final assessment grade updated but course grade cannot be calculated
                messages.success(request, 'Final Grade Updated Successfully')
                return redirect(reverse('chemapp:student', kwargs={'student_id': student_id, }))
            else:
                courseGrade = 0
                for assessmentGrade in assessmentGrades:
                    weight = assessmentGrade.assessment.weight
                    weightedGrade = weight * assessmentGrade.finalGrade22Scale
                    courseGrade = courseGrade + weightedGrade

                courseGrade = round(courseGrade)
                band = GRADE_TO_BAND[courseGrade]

                courseGradeObject = CourseGrade.objects.create(course=course, student=student, grade=courseGrade,
                                                               band=band)

                # Success message
                # Final assessment grade updated and course grade calculated
                messages.success(request, 'Final Grade Updated Successfully and Course Grade Calculated!')
                return redirect(reverse('chemapp:student', kwargs={'student_id': student_id, }))

        else:
            print(final_grade_form.errors)

    else:
        final_grade_form = FinalAssessmentGradeForm(instance=assessmentGrade)

    addfinalGradeDict['final_grade_form'] = final_grade_form
    return render(request, 'chemapp/edit_final_grade.html', context=addfinalGradeDict)


@login_required
def delete_final_grade(request, student_id, course_name_slug, assessment_name_slug):
    student = Student.objects.get(studentID=student_id)
    course = Course.objects.get(slug=course_name_slug)
    assessment = Assessment.objects.get(course=course, slug=assessment_name_slug)
    assessmentGrade = AssessmentGrade.objects.get(assessment=assessment, student=student)

    if request.method == 'POST':
        # Delete Final Assessment Grade by updating Assessment Grade
        assessmentGrade.finalGrade = None
        assessmentGrade.finalGrade22Scale = None
        assessmentGrade.band = None

        assessmentGrade.save()

        # Delete Course Grade if possible
        try:
            courseGrade = CourseGrade.objects.get(course=course, student=student)
            courseGrade.delete()
        except CourseGrade.DoesNotExist:
            pass

        messages.success(request, 'Final Grade deleted successfully!')
        return redirect(reverse('chemapp:student', kwargs={'student_id': student_id, }))

    return render(request, 'chemapp/student.html', context={})


@login_required
@permission_required_context('chemapp.add_student', 'No permission to add_student', raise_exception=True)
def upload_student_csv(request, course_name_slug):
    # student_dict = {'boldmessage':'Upload csv file to add students'}
    # return render(request,'chemapp/upload_student_csv.html', context=student_dict)
    template = 'chemapp/upload_student_csv.html'
    data = Student.objects.all()
    uploadStudents = {}
    uploadStudents['course_name_slug'] = course_name_slug
    course = Course.objects.get(slug=course_name_slug)
    if request.method == "GET":
        return render(request, template)

    csv_file = request.FILES['file']
    if not csv_file.name.endswith('.csv'):
        messages.error(request, 'THIS IS NOT A CSV FILE')
        return render(request, 'chemapp/upload_student_csv.html', context=uploadStudents)

    data_set = csv_file.read().decode('UTF-8')
    io_string = io.StringIO(data_set)
    next(io_string)
    for column in csv.reader(io_string, delimiter=',', quotechar="|"):
        if not Student.objects.filter(studentID=column[0]).exists():
            degree = Degree.objects.get(degreeCode=column[3])
            degree.numberOfStudents += 1
            degree.save()
        if not Student.objects.filter(studentID=column[0], courses=course).exists():
            course.numberOfStudents += 1
            course.save()
        _, created = Student.objects.update_or_create(
            studentID=column[0],
            defaults={'firstName': column[1],
                      'lastName': column[2],
                      'academicPlan': Degree.objects.get(degreeCode=column[3]),
                      'level': column[4],
                      'graduationDate': column[6],
                      'anonID': column[5],
                      }
        )
        student = Student.objects.get(studentID=column[0])
        student.courses.add(course)
        student.save()

    context = {}
    messages.success(request, "Student Added Successfully")
    return render(request, 'chemapp/upload_student_csv.html', context=uploadStudents)


@login_required
@permission_required_context('chemapp.add_degree', 'No permission to add_degree', raise_exception=True)
def upload_degree_csv(request):
    template = 'chemapp/upload_degree_csv.html'
    data = Degree.objects.all()

    if request.method == "GET":
        return render(request, template)

    csv_file = request.FILES['file']
    if not csv_file.name.endswith('.csv'):
        messages.error(request, 'THIS IS NOT A CSV FILE')
        return redirect(reverse('chemapp:degrees'))

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
@permission_required_context('chemapp.add_course', 'No permission to add_course', raise_exception=True)
def upload_course_csv(request):
    template = 'chemapp/upload_course_csv.html'
    data = Course.objects.all()

    if request.method == "GET":
        return render(request, template)

    csv_file = request.FILES['file']
    if not csv_file.name.endswith('.csv'):
        messages.error(request, 'THIS IS NOT A CSV FILE')
        return redirect('chemapp:upload_course_csv')

    data_set = csv_file.read().decode('UTF-8')
    io_string = io.StringIO(data_set)
    next(io_string)
    for column in csv.reader(io_string, delimiter=',', quotechar="|"):
        if not Degree.objects.filter(degreeCode=column[1]).exists():
            messages.error(request, 'The degree does not exist, unable to upload courses csv file')
            return redirect(reverse('chemapp:courses'))
        else:
            if not Course.objects.filter(code=column[0]).exists():
                degree = Degree.objects.get(degreeCode=column[1])
                degree.numberOfCourses = degree.numberOfCourses + 1
                degree.save()
            _, created = Course.objects.update_or_create(
                code=column[0],
                degree=Degree.objects.get(degreeCode=column[1]),
                defaults={'creditsWorth': column[2],
                          'name': column[3],
                          'shortHand': column[4],
                          'level': column[5],
                          'year': column[6],
                          'academicYearTaught': column[7],
                          'semester': column[8],
                          'minimumPassGrade': column[9],
                          'minimumRequirementsForCredit': column[10],
                          'description': column[11],
                          'comments': column[12],
                          }

            )

    context = {}
    messages.success(request, "Courses Added Successfully")
    return redirect(reverse('chemapp:courses'))


@login_required
@permission_required_context('chemapp.add_assessments', 'No permission to add_assessments', raise_exception=True)
def upload_assessment_csv(request, course_name_slug):
    template = 'chemapp/upload_assessment_csv.html'
    data = Assessment.objects.all()
    weightsum = 0

    if request.method == "GET":
        return render(request, template)

    csv_file = request.FILES['file']
    if not csv_file.name.endswith('.csv'):
        messages.error(request, 'THIS IS NOT A CSV FILE')
        return redirect(reverse('chemapp:course', kwargs={'course_name_slug': course_name_slug}))

    data_set = csv_file.read().decode('UTF-8')
    io_string = io.StringIO(data_set)
    next(io_string)

    exams = []
    examNames = []

    # weight has to be equal to 1
    # cannot have duplicate names
    for column in csv.reader(io_string, delimiter=',', quotechar="|"):
        weightsum += float(column[2])
        if column[0] in examNames:
            messages.error(request, 'Duplicate Assessment Detected')
            return redirect(reverse('chemapp:course', kwargs={'course_name_slug': course_name_slug}))

        examNames.append(column[0])
        exams.append(column)

    if weightsum != 1:
        messages.error(request, 'The sum of the Assessment Weights must be equal to 1')
        return redirect(reverse('chemapp:course', kwargs={'course_name_slug': course_name_slug}))

    for exam in exams:
        # Converts date string to datetime object
        dueDateString = exam[3]
        dueDate = datetime.strptime(dueDateString, '%d/%m/%Y %H:%M')  # Unaware datetime object
        dueDate = dueDate.replace(tzinfo=pytz.UTC)  # Aware datetime object

        _, created = Assessment.objects.update_or_create(
            assessmentName=exam[0],
            course=Course.objects.get(slug=course_name_slug),
            defaults={'totalMarks': exam[1],
                      'componentNumberNeeded': exam[4],
                      'dueDate': dueDate,
                      'weight': exam[2],
                      }
        )
    else:
        messages.success(request, "Assessment Added Successfully")
        return redirect(reverse('chemapp:course', kwargs={'course_name_slug': course_name_slug}))


@login_required
@permission_required_context('chemapp.add_assessmentComponents', 'No permission to add_assessmentComponents',
                             raise_exception=True)
def upload_assessment_comp_csv(request, course_name_slug, assessment_name_slug):
    template = 'chemapp/upload_assessment_comp_csv.html'
    data = AssessmentComponent.objects.all()
    totalmarks = 0
    course = Course.objects.get(slug=course_name_slug)

    if request.method == "GET":
        return render(request, template)

    csv_file = request.FILES['file']
    if not csv_file.name.endswith('.csv'):
        messages.error(request, 'THIS IS NOT A CSV FILE')
        return redirect(reverse('chemapp:course', kwargs={'course_name_slug': course_name_slug}))

    data_set = csv_file.read().decode('UTF-8')
    io_string = io.StringIO(data_set)
    next(io_string)

    for column in csv.reader(io_string, delimiter=',', quotechar="|"):
        totalmarks = totalmarks + int(column[2])
        _, created = AssessmentComponent.objects.update_or_create(
            description=column[0],
            required=column[1],
            marks=column[2],
            assessment=Assessment.objects.get(slug=assessment_name_slug, course=course),
        )

    assessment = Assessment.objects.get(slug=assessment_name_slug, course=course)
    if totalmarks != assessment.totalMarks:
        AssessmentComponent.objects.filter(assessment=assessment).delete()
        messages.error(request, 'The sum of the Assessment Components must be equal to %s' % assessment.totalMarks)
        return redirect(reverse('chemapp:course', kwargs={'course_name_slug': course_name_slug}))

    messages.success(request, "Assessment Components Added Successfully")
    return redirect(reverse('chemapp:course', kwargs={'course_name_slug': course_name_slug}))


@login_required
@permission_required_context('chemapp.add_assessmentComponents', 'No permission to add_grades', raise_exception=True)
def upload_grades_csv(request, course_code, assessment_name):
    template = 'chemapp/upload_grades_csv.html'
    data = AssessmentComponentGrade.objects.all()
    course = Course.objects.get(code=course_code)
    assessment = Assessment.objects.get(assessmentName=assessment_name, course=course)
    component = AssessmentComponent.objects.get(assessment=assessment)

    if request.method == "GET":
        return render(request, template)

    csv_file = request.FILES['file']
    if not csv_file.name.endswith('.csv'):
        messages.error(request, 'THIS IS NOT A CSV FILE')
        return redirect(reverse('chemapp:courses'))

    data_set = csv_file.read().decode('UTF-8')
    io_string = io.StringIO(data_set)
    next(io_string)
    for column in csv.reader(io_string, delimiter=',', quotechar="|"):
        if int(column[2]) > component.marks:
            messages.error(request,
                           'Student with ID number: %s has been awarded a grade higher than %s which is the highest mark available' % (
                               column[0], component.marks))
            return redirect(reverse('chemapp:courses'))
        elif not AssessmentComponent.objects.filter(description=column[1]).exists():
            messages.error(request, '%s is not an assessment component' % column[1])
            return redirect(reverse('chemapp:courses'))
        _, created = AssessmentComponentGrade.objects.update_or_create(
            student=Student.objects.get(studentID=column[0]),
            assessmentComponent=AssessmentComponent.objects.get(description=column[1]),
            grade=column[2],
        )

    messages.success(request, "Grades Added Successfully")
    return redirect(reverse('chemapp:courses'))


@login_required
def staff(request):
    StaffDict = {}
    # checking order by
    staff = Staff.objects.order_by('lastName')
    StaffDict['staff'] = staff

    return render(request, 'chemapp/staff.html', context=StaffDict)


@login_required
def add_staff(request):
    addStaffDict = {}

    if request.method == 'POST':
        staff_form = StaffForm(request.POST)
        if staff_form.is_valid():
            staffID = staff_form.cleaned_data.get('staffID')
            title = staff_form.cleaned_data.get('title')
            firstName = staff_form.cleaned_data.get('firstName')
            lastName = staff_form.cleaned_data.get('lastName')
            comments = staff_form.cleaned_data.get('comments')
            username = firstName + lastName
            user_object = User.objects.create_user(username, password=str(staffID))
            # Check if Course has already been added
            try:
                staff = Staff.objects.get(staffID=staffID)
                messages.error(request, 'Staff has already been added!')
                return redirect(reverse('chemapp:add_staff'))
            except Staff.DoesNotExist:
                pass

            staff = staff_form.save()
            messages.success(request, "Staff Added Successfully")
            return redirect(reverse('chemapp:staff'))
        else:
            print(staff_form.errors)
    else:
        staff_form = StaffForm()

    addStaffDict['staff_form'] = staff_form
    return render(request, 'chemapp/add_staff.html', context=addStaffDict)


def staff_member(request, staffID):
    staff_memberDict = {}
    try:
        staff = Staff.objects.get(staffID=staffID)
        courses = Course.objects.filter(lecturers__staffID=staffID)
        staff_memberDict['courses'] = courses
        staff_memberDict['staff'] = staff
        staff_memberDict['courses'] = {}
        staff_memberDict['staffID'] = staffID

    except Staff.DoesNotExist:
        raise Http404("Staff member does not exist")
    return render(request, 'chemapp/staff_member.html', context=staff_memberDict)


@login_required
def edit_staff(request, staffID):
    editStaffDict = {}
    editStaffDict['staffID'] = staffID
    staff = Staff.objects.get(staffID=staffID)

    if (request.method == 'POST'):
        edit_staff_form = EditStaffForm(request.POST)

        if edit_staff_form.is_valid():
            title = edit_staff_form.cleaned_data.get('title')
            firstName = edit_staff_form.cleaned_data.get('firstName')
            lastName = edit_staff_form.cleaned_data.get('lastName')
            comments = edit_staff_form.cleaned_data.get('comments')

            staff.title = title
            staff.firstName = firstName
            staff.lastName = lastName
            staff.comments = comments

            staff.save()

            messages.success(request, 'Staff data was updated successfully!')
            return redirect(reverse('chemapp:staff_member', kwargs={'staffID': staffID}))
        else:
            print(edit_staff_form.errors)
    else:
        edit_staff_form = EditStaffForm(instance=staff)

    editStaffDict['edit_staff_form'] = edit_staff_form

    return render(request, 'chemapp/edit_staff.html', context=editStaffDict)


def search_site(request):
    if request.method == 'GET':
        query = request.GET.get('q')

        submitbutton = request.GET.get('submit')

        if query is not None:
            course_lookups = Q(name__icontains=query) | Q(code__icontains=query) | Q(shortHand__icontains=query)
            student_lookups = Q(studentID__icontains=query) | Q(firstName__icontains=query) | Q(
                lastName__icontains=query)
            staff_lookups = Q(staffID__icontains=query) | Q(firstName__icontains=query) | Q(lastName__icontains=query)

            course_results = Course.objects.filter(course_lookups).distinct()
            student_results = Student.objects.filter(student_lookups).distinct()
            staff_results = Staff.objects.filter(staff_lookups).distinct()
            results = [course_results, student_results, staff_results]
            context = {'staff_results': staff_results, 'course_results': course_results,
                       'student_results': student_results,
                       'submitbutton': submitbutton}

            return render(request, 'chemapp/search_site.html', context)

        else:
            return render(request, 'chemapp/search_site.html')

    else:
        return render(request, 'chemapp/search_site.html')
