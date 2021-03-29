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
from decimal import *
from .admin import CourseGrade
import json

GRADE_TO_BAND = {22: 'A1', 21: 'A2', 20: 'A3', 19: 'A4', 18: 'A5',
                 17: 'B1', 16: 'B2', 15: 'B3',
                 14: 'C1', 13: 'C2', 12: 'C3',
                 11: 'D1', 10: 'D2', 9: 'D3',
                 8: 'E1', 7: 'E2', 6: 'E3',
                 5: 'F1', 4: 'F2', 3: 'F3',
                 2: 'G1', 1: 'G2', 0: 'H',
                 }


def addCoursePermissions(course_slug):
    course_slug = course_slug.upper()
    content_type = ContentType.objects.get_for_model(Course)
    Permission.objects.create(codename='can_edit_course' + course_slug, name="can edit course " + course_slug,
                              content_type=content_type, )
    Permission.objects.create(codename='can_upload_grades_for' + course_slug,
                              name="can upload grades for " + course_slug, content_type=content_type, )
    return


def removeCoursePermissions(course_slug):
    course_slug = course_slug.upper()
    content_type = ContentType.objects.get_for_model(Course)
    Permission.objects.filter(codename='can_edit_course' + course_slug, name="can edit course " + course_slug,
                              content_type=content_type, ).delete()
    Permission.objects.filter(codename='can_upload_grades_for' + course_slug,
                              name="can upload grades for " + course_slug, content_type=content_type, ).delete()
    return


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
                degreeCode = form.cleaned_data.get('degreeCode').upper()
                name = form.cleaned_data.get('name')
                slug = slugify(degreeCode)

                # Check if Degree already exists
                try:
                    degree = Degree.objects.get(degreeCode=degreeCode)
                    messages.error(request, "Degree with code: " + degreeCode + " already exists!")
                    return redirect(reverse('chemapp:add_degree'))
                except Degree.DoesNotExist:
                    pass

                if degreeCode in codes:
                    messages.error(request, "Duplicate degree " + degreeCode + " was only added once!")
                else:
                    codes.append(degreeCode)
                    degrees.append(Degree(degreeCode=degreeCode,
                                          name=name,
                                          slug=slug,
                                          numberOfCourses=0,
                                          numberOfStudents=0))

            Degree.objects.bulk_create(degrees)

            messages.success(request, "Degrees Added Successfully!")
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
    delDegree = Degree.objects.get(slug=degree_code_slug)

    if request.method == 'POST':
        courses = Course.objects.filter(degree=delDegree)

        for course in courses:
            removeCoursePermissions(course.slug)

        delDegree.delete()

        messages.success(request, 'Degree deleted successfully!')
        return redirect(reverse('chemapp:degrees'))

    return render(request, 'chemapp/degrees.html', context={})


@login_required
@permission_required_context('chemapp.add_degree', 'No permission to add_degree', raise_exception=True)
def upload_degree_csv(request):
    if request.method == "GET":
        return render(request, 'chemapp/upload_degree_csv.html')

    csv_file = request.FILES['file']
    if not csv_file.name.endswith('.csv'):
        messages.error(request, 'THIS IS NOT A CSV FILE')
        return redirect(reverse('chemapp:degrees'))

    data_set = csv_file.read().decode('UTF-8')
    io_string = io.StringIO(data_set)
    next(io_string)
    for column in csv.reader(io_string, delimiter=',', quotechar="|"):
        created = Degree.objects.update_or_create(
            degreeCode=column[0],
            defaults={'name': column[1],
                      }
        )

    messages.success(request, "Degrees Added Successfully!")
    return redirect(reverse('chemapp:degrees'))


@login_required
def courses(request):
    coursesDict = {}
    courses = Course.objects.all()

    levelDict = {}

    for course in courses:
        slug = course.slug
        code = course.code
        color = course.courseColor
        level = course.level
        name = course.name

        if level not in levelDict.values():
            levelDict[level] = level

        courseList = [level, slug, code, color, name]

        coursesDict[course] = courseList

    return render(request, 'chemapp/courses.html', {'courses': coursesDict, 'levels': levelDict})


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
def export_course_grades(request, course_name_slug):
    course = Course.objects.get(slug=course_name_slug)
    students = Student.objects.filter(courses=course)

    response = HttpResponse(content_type='text/csv')
    # Bug will occur in 79 years :)
    academicYear = '20' + course.academicYearTaught[:2]
    filename = course.code + '_' + academicYear
    response['Content-Disposition'] = 'attachment; filename=' + '"' + filename + '.csv"'

    writer = csv.writer(response)
    writer.writerow(['Course', 'Degree', 'AcademicYear', 'ANONID', 'EMPLID', 'Name', 'Grade'])
    for student in students:
        studentName = student.firstName + ',' + student.lastName
        try:
            courseGrade = CourseGrade.objects.get(course=course, student=student)
            band = courseGrade.band
        except CourseGrade.DoesNotExist:
            band = 'NA'

        writer.writerow([course.code, course.degree, course.academicYearTaught, student.anonID,
                         student.studentID, studentName, band])

    return response


@login_required
def export_assessment_grades(request, course_name_slug, assessment_name_slug):
    course = Course.objects.get(slug=course_name_slug)
    assessment = Assessment.objects.get(course=course, slug=assessment_name_slug)
    components = AssessmentComponent.objects.filter(assessment=assessment)
    students = Student.objects.filter(courses=course)

    response = HttpResponse(content_type='text/csv')
    # Bug will occur in 79 years :)
    academicYear = '20' + course.academicYearTaught[:2]
    filename = course.code + '_' + academicYear + '_' + assessment.assessmentName
    response['Content-Disposition'] = 'attachment; filename=' + '"' + filename + '.csv"'

    writer = csv.writer(response)

    columns = ['Course', 'Degree', 'AcademicYear', 'ANONID', 'EMPLID', 'Name']
    for component in components:
        columns.append(component.description)

    columns.append('Overall Assessment Grade')

    writer.writerow(columns)
    for student in students:
        studentName = student.firstName + ',' + student.lastName
        data = [course.code, course.degree, course.academicYearTaught, student.anonID, student.studentID, studentName]

        # Get Component Grades
        for component in components:
            try:
                componentGrade = AssessmentComponentGrade.objects.get(assessmentComponent=component, student=student)
                grade = componentGrade.grade
                if grade is None:
                    grade = 'NA'
            except AssessmentComponentGrade.DoesNotExist:
                grade = 'NA'
            data.append(grade)

        # Get Assessment Grade
        try:
            assessmentGrade = AssessmentGrade.objects.get(assessment=assessment, student=student)
            assessmentBand = assessmentGrade.band
        except AssessmentGrade.DoesNotExist:
            assessmentBand = 'NA'
        data.append(assessmentBand)

        writer.writerow(data)

    return response


@login_required
def course_students(request, course_name_slug):
    course = Course.objects.get(slug=course_name_slug)
    students = Student.objects.filter(courses=course)

    courseStudentsDict = {}
    courseStudentsDict['course_name_slug'] = course_name_slug
    courseStudentsDict['students'] = students
    courseStudentsDict['course_code'] = course.code

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

            # Check for a valid Pass Grade
            minimumPassGrade = course_form.cleaned_data.get('minimumPassGrade').upper()
            if minimumPassGrade not in GRADE_TO_BAND.values():
                messages.error(request, (str(minimumPassGrade) + ' is not a valid grade!'))
                return redirect(reverse('chemapp:add_course'))

            course = course_form.save()
            course_slug = course.slug

            addCoursePermissions(course_slug)

            # Increment degree course count
            degree = course.degree
            degree.numberOfCourses = degree.numberOfCourses + 1
            degree.save()

            # Success message
            messages.success(request, "Course added successfully!")
            return redirect(reverse('chemapp:course', kwargs={'course_name_slug': course_slug}))

        else:
            messages.error(request, 'Course has already been added!')
            print(course_form.errors)
    else:
        course_form = CourseForm()

    addCourseDict['course_form'] = CourseForm()

    return render(request, 'chemapp/add_course.html', context=addCourseDict)


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
            lecturers = edit_course_form.cleaned_data.get('lecturers')

            # Check for a valid Pass Grade
            if minimumPassGrade.upper() not in GRADE_TO_BAND.values():
                messages.error(request, (str(minimumPassGrade) + ' is not a valid grade!'))
                return redirect(reverse('chemapp:add_course'))

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
            course.lecturers.set(lecturers)

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

        removeCoursePermissions(course_name_slug)

        messages.success(request, 'Course deleted successfully!')
        return redirect(reverse('chemapp:courses'))

    return render(request, 'chemapp/course.html', context={})


@login_required
@permission_required_context('chemapp.add_course', 'No permission to add_course', raise_exception=True)
def upload_course_csv(request):
    if request.method == "GET":
        return render(request, 'chemapp/upload_course_csv.html')

    csv_file = request.FILES['file']
    if not csv_file.name.endswith('.csv'):
        messages.error(request, 'THIS IS NOT A CSV FILE')
        return redirect('chemapp:upload_course_csv')

    data_set = csv_file.read().decode('UTF-8')
    io_string = io.StringIO(data_set)
    next(io_string)
    for column in csv.reader(io_string, delimiter=',', quotechar="|"):
        if not Degree.objects.filter(degreeCode=column[1]).exists():
            messages.error(request,
                           'Degree with code: ' + column[1] + ' does not exist, unable to upload courses csv file')
            return redirect(reverse('chemapp:courses'))

        if not Course.objects.filter(code=column[0]).exists():
            # Increment degree course count
            degree = Degree.objects.get(degreeCode=column[1])
            degree.numberOfCourses = degree.numberOfCourses + 1
            degree.save()

            course_slug = slugify(str(column[0]) + "-" + str(column[1]))

            addCoursePermissions(course_slug)

            created = Course.objects.update_or_create(
                code=column[0],
                degree=Degree.objects.get(degreeCode=column[1]),
                defaults={'creditsWorth': column[2],
                          'name': column[3],
                          'shortHand': column[4],
                          'level': column[5],
                          'academicYearTaught': column[6],
                          'semester': column[7],
                          'minimumPassGrade': column[8],
                          'minimumRequirementsForCredit': column[9],
                          'description': column[10],
                          'comments': column[11],
                          }
            )

    messages.success(request, "Courses Added Successfully!")
    return redirect(reverse('chemapp:courses'))


@login_required
@permission_required_context('chemapp.add_assessments', 'No permission to add_assessments', raise_exception=True)
def add_assessments(request, course_name_slug):
    AssessmentFormSet = formset_factory(AssessmentForm, extra=1)
    course = Course.objects.get(slug=course_name_slug)
    existingAssessments = Assessment.objects.filter(course=course)

    addAssessmentsDict = {}
    addAssessmentsDict['course_name_slug'] = course_name_slug
    addAssessmentsDict['existingAssessments'] = existingAssessments

    if (request.method == 'POST'):
        assessment_formset = AssessmentFormSet(request.POST)

        if assessment_formset.is_valid():
            assessments = []

            # This is used to check for Assessment duplicates
            assessmentNames = []
            # This is used to check that the Assessment weight sum is equal to 1 in the end
            weightSum = 0
            # Calculates current weight Sum with existing Assessments
            for assessment in existingAssessments:
                weightSum += assessment.weight

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
                    messages.error(request, 'Assessment ' + str(name) + ' has already been added!')
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
                                                  slug=slug,
                                                  map=None))

            # Check that the weights add to 1
            if weightSum != 1:
                messages.error(request, 'The sum of the Assessment Weights must be equal to 1')
                return redirect(reverse('chemapp:add_assessments', kwargs={'course_name_slug': course_name_slug}))
            else:
                Assessment.objects.bulk_create(assessments)
                assessmentsCreated = Assessment.objects.filter(course=course)

                # Success message
                messages.success(request, "Assessments added successfully!")
                return redirect(reverse('chemapp:course', kwargs={'course_name_slug': course_name_slug}))
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
@permission_required_context('chemapp.add_assessments', 'No permission to add_assessments', raise_exception=True)
def upload_assessment_csv(request, course_name_slug):
    uploadAssessments = {}
    uploadAssessments['course_name_slug'] = course_name_slug

    if request.method == "GET":
        return render(request, 'chemapp/upload_assessment_csv.html', context=uploadAssessments)

    csv_file = request.FILES['file']
    if not csv_file.name.endswith('.csv'):
        messages.error(request, 'THIS IS NOT A CSV FILE')
        return redirect(reverse('chemapp:upload_assessment_csv', kwargs={'course_name_slug': course_name_slug}))

    data_set = csv_file.read().decode('UTF-8')
    io_string = io.StringIO(data_set)
    next(io_string)

    # Calculates current Weight Sum with existing Assessments
    course = Course.objects.get(slug=course_name_slug)
    weightsum = 0

    courseAssessments = Assessment.objects.filter(course=course)
    for assessment in courseAssessments:
        weightsum += assessment.weight

    assessments = []
    assessmentNames = []

    for column in csv.reader(io_string, delimiter=',', quotechar="|"):
        weightsum += Decimal(column[2])
        # Cannot have duplicate Assessments
        if column[0] in assessmentNames:
            messages.error(request, 'Duplicate Assessment ' + column[0])
            return redirect(reverse('chemapp:upload_assessment_csv', kwargs={'course_name_slug': course_name_slug}))

        assessmentNames.append(column[0])
        assessments.append(column)

    # The sum of the weight of all Assessments must be equal to 1
    if weightsum != 1:
        messages.error(request, 'The sum of the Assessment Weights must be equal to 1')
        return redirect(reverse('chemapp:upload_assessment_csv', kwargs={'course_name_slug': course_name_slug}))

    for assessment in assessments:
        # Converts date string to datetime object
        dueDateString = assessment[3]
        dueDate = datetime.strptime(dueDateString, '%d/%m/%Y %H:%M')  # Unaware datetime object
        dueDate = dueDate.replace(tzinfo=pytz.UTC)  # Aware datetime object

        created = Assessment.objects.update_or_create(
            assessmentName=assessment[0],
            course=Course.objects.get(slug=course_name_slug),
            defaults={'totalMarks': assessment[1],
                      'componentNumberNeeded': assessment[4],
                      'dueDate': dueDate,
                      'weight': assessment[2],
                      }
        )
    else:
        messages.success(request, "Assessments Added Successfully")
        return redirect(reverse('chemapp:course', kwargs={'course_name_slug': course_name_slug}))


@login_required
def map(request, course_name_slug, assessment_name_slug):
    course = Course.objects.get(slug=course_name_slug)
    assessment = Assessment.objects.get(course=course, slug=assessment_name_slug)

    mapDict = {}
    mapDict['course_name_slug'] = course_name_slug
    mapDict['assessment_name_slug'] = assessment_name_slug

    if assessment.map is None:
        mapDict['mapList'] = None
    else:
        jsonDec = json.decoder.JSONDecoder()
        mapList = jsonDec.decode(assessment.map)
        mapDict['mapList'] = mapList

    return render(request, 'chemapp/map.html', context=mapDict)


@login_required
def upload_map_csv(request, course_name_slug, assessment_name_slug):
    uploadMapDict = {}
    uploadMapDict['course_name_slug'] = course_name_slug
    uploadMapDict['assessment_name_slug'] = assessment_name_slug

    course = Course.objects.get(slug=course_name_slug)
    assessment = Assessment.objects.get(slug=assessment_name_slug, course=course)

    mapList = []

    if request.method == "GET":
        return render(request, 'chemapp/upload_map_csv.html', context=uploadMapDict)

    csv_file = request.FILES['file']
    if not csv_file.name.endswith('.csv'):
        messages.error(request, 'THIS IS NOT A CSV FILE')
        return redirect(reverse('chemapp:upload_map_csv', kwargs={'course_name_slug': course_name_slug,
                                                                  'assessment_name_slug': assessment_name_slug}))

    data_set = csv_file.read().decode('UTF-8')
    io_string = io.StringIO(data_set)
    next(io_string)
    for column in csv.reader(io_string, delimiter=',', quotechar="|"):
        scale = column[0]
        mapList.append(scale)

    if len(mapList) != 101:
        messages.error(request, "Incorrect Map Size!")
        return redirect(reverse('chemapp:upload_map_csv', kwargs={'course_name_slug': course_name_slug,
                                                                  'assessment_name_slug': assessment_name_slug}))
    else:
        assessment.map = json.dumps(mapList)
        assessment.save()

    messages.success(request, "Map Added Successfully!")
    return redirect(reverse('chemapp:map', kwargs={'course_name_slug': course_name_slug,
                                                   'assessment_name_slug': assessment_name_slug}))


@login_required
@permission_required_context('chemapp.add_assessmentComponents', 'No permission to add_assessmentComponents',
                             raise_exception=True)
def add_assessmentComponents(request, course_name_slug, assessment_name_slug):
    AssessmentComponentFormSet = formset_factory(AssessmentComponentForm, extra=1)
    course = Course.objects.get(slug=course_name_slug)
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
                lecturer = form.cleaned_data.get('lecturer')
                marks = form.cleaned_data.get('marks')
                description = form.cleaned_data.get('description')
                slug = slugify(description)

                if required is True:
                    status = 'Required'
                else:
                    status = 'Optional'

                # Check if Assessment Component has already been added
                try:
                    component = AssessmentComponent.objects.get(assessment=assessment, description=description)
                    messages.error(request,
                                   'Assessment Component ' + str(description) + ' has already been added!')
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
                                                                    lecturer=lecturer,
                                                                    slug=slug,
                                                                    assessment=assessment))

            AssessmentComponent.objects.bulk_create(assessmentComponents)

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
            lecturer = edit_component_form.cleaned_data.get('lecturer')

            component.required = required
            component.marks = marks
            component.lecturer = lecturer

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


@login_required
@permission_required_context('chemapp.add_assessmentComponents', 'No permission to add_assessmentComponents',
                             raise_exception=True)
def upload_assessment_comp_csv(request, course_name_slug, assessment_name_slug):
    course = Course.objects.get(slug=course_name_slug)
    assessment = Assessment.objects.get(slug=assessment_name_slug, course=course)

    uploadAssessmentComponents = {}
    uploadAssessmentComponents['course_name_slug'] = course_name_slug
    uploadAssessmentComponents['assessment_name_slug'] = assessment_name_slug

    if request.method == "GET":
        return render(request, 'chemapp/upload_assessment_comp_csv.html', context=uploadAssessmentComponents)

    csv_file = request.FILES['file']
    if not csv_file.name.endswith('.csv'):
        messages.error(request, 'THIS IS NOT A CSV FILE')
        return redirect(reverse('chemapp:upload_assessment_comp_csv', kwargs={'course_name_slug': course_name_slug,
                                                                              'assessment_name_slug': assessment_name_slug}))

    data_set = csv_file.read().decode('UTF-8')
    io_string = io.StringIO(data_set)
    next(io_string)

    for column in csv.reader(io_string, delimiter=',', quotechar="|"):
        required_optional = column[1]
        if required_optional == "Required":
            required = True
        else:
            required = False

        # Check if Lecturer Exists
        try:
            lecturer = Staff.objects.get(username=column[3].replace(" ", ""))
        except Staff.DoesNotExist:
            messages.error(request, 'Lecturer ' + str(column[3]) + ' does not exist!')
            return redirect(reverse('chemapp:upload_assessment_comp_csv', kwargs={'course_name_slug': course_name_slug,
                                                                                  'assessment_name_slug': assessment_name_slug}))

        created = AssessmentComponent.objects.update_or_create(
            description=column[0],
            assessment=assessment,
            defaults={'required': required,
                      'marks': column[2],
                      'lecturer': lecturer,
                      }
        )

    assessment = Assessment.objects.get(slug=assessment_name_slug, course=course)

    messages.success(request, "Assessment Components Added Successfully")
    return redirect(reverse('chemapp:course', kwargs={'course_name_slug': course_name_slug}))


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
            student = student_form.save()

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
            student_id = student.studentID
            messages.success(request, "Student Added Successfully!")
            return redirect(reverse('chemapp:student', kwargs={'student_id': student_id}))

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
        return redirect(reverse('chemapp:courses'))

    return render(request, 'chemapp/student.html', context={})


@login_required
@permission_required_context('chemapp.add_student', 'No permission to add_student', raise_exception=True)
def upload_student_csv(request, course_name_slug):
    course = Course.objects.get(slug=course_name_slug)

    uploadStudents = {}
    uploadStudents['course_name_slug'] = course_name_slug

    if request.method == "GET":
        return render(request, 'chemapp/upload_student_csv.html', context=uploadStudents)

    csv_file = request.FILES['file']
    # Check if this is a CSV file
    if not csv_file.name.endswith('.csv'):
        messages.error(request, 'THIS IS NOT A CSV FILE')
        return render(request, 'chemapp/upload_student_csv.html', context=uploadStudents)

    data_set = csv_file.read().decode('UTF-8')
    io_string = io.StringIO(data_set)
    next(io_string)
    for column in csv.reader(io_string, delimiter=',', quotechar="|"):
        # Check if this Student already exists
        try:
            student = Student.objects.get(studentID=column[0])
        except Student.DoesNotExist:
            try:
                degree = Degree.objects.get(degreeCode=column[3])
                degree.numberOfStudents += 1
                degree.save()
            except Degree.DoesNotExist:
                messages.error(request, 'Degree ' + column[3] + ' does not exist, unable to upload students csv file')
                return redirect(reverse('chemapp:course_students', kwargs={'course_name_slug': course_name_slug}))

            course.numberOfStudents += 1
            course.save()

        # Converts date string to datetime object
        graduationDateString = column[5]
        graduationDate = datetime.strptime(graduationDateString, '%d/%m/%Y')

        created = Student.objects.update_or_create(
            studentID=column[0],
            defaults={'firstName': column[1],
                      'lastName': column[2],
                      'academicPlan': Degree.objects.get(degreeCode=column[3]),
                      'level': column[4],
                      'graduationDate': graduationDate,
                      }
        )
        student = Student.objects.get(studentID=column[0])
        student.courses.add(course)
        student.save()

    messages.success(request, "Student Added Successfully!")
    return redirect(reverse('chemapp:course_students', kwargs={'course_name_slug': course_name_slug}))


@login_required
def ajax_filter_courses(request):
    degree = request.GET.get('degree')
    courses = Course.objects.filter(degree=degree).order_by('level')
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
                if assessmentComponent.required is True and grade is None:
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
                assessmentComponentGrade = AssessmentComponentGrade.objects.get(assessmentComponent=component,
                                                                                student=student)
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
                                           finalGradePercentage=None,
                                           finalGrade22Scale=None,
                                           band=None,
                                           componentNumberAnswered=count,
                                           componentNumberMatch=componentNumberMatch,
                                           late=late,
                                           assessment=assessment,
                                           student=student)

            # Success message
            messages.success(request, 'Grades Added Successfully!')
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
                if assessmentComponent.required is True and grade is None:
                    messages.error(request, 'Grade for ' + str(assessmentComponent.description) + ' is required!')
                    return redirect(reverse('chemapp:edit_grades', kwargs={'student_id': student_id,
                                                                           'course_name_slug': course_name_slug,
                                                                           'assessment_name_slug': assessment_name_slug}))
                else:
                    pass

                # Check if supplied grade is more than the available marks
                if grade is not None and grade > assessmentComponent.marks:
                    messages.error(request,
                                   'Grade for ' + str(assessmentComponent.description) + ' exceeds available marks!')
                    return redirect(reverse('chemapp:edit_grades', kwargs={'student_id': student_id,
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
                assessmentComponentGrade = AssessmentComponentGrade.objects.get(assessmentComponent=component,
                                                                                student=student)
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
            assessmentGrade.finalGradePercentage = None
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
            messages.success(request, 'Grades Updated Successfully!')
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
            try:
                assessmentComponentGrade = AssessmentComponentGrade.objects.get(assessmentComponent=component,
                                                                                student=student)
                assessmentComponentGrade.delete()
            except AssessmentComponentGrade.DoesNotExist:
                pass

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

            # Check if Final Grade is more than the available Assessment Marks
            assessmentMarks = assessment.totalMarks
            if finalGrade > assessmentMarks:
                messages.error(request, 'Final Grade exceeds Available Assessment Marks!')
                return redirect(reverse('chemapp:add_final_grade',
                                        kwargs={'student_id': student_id, 'course_name_slug': course_name_slug,
                                                'assessment_name_slug': assessment_name_slug}))

            # Convert final grade to Percentage
            finalGradePercentage = (finalGrade * 100) / assessment.totalMarks
            roundedFinalGradePercentage = round(finalGradePercentage)

            # Check if Map has been uploaded
            if assessment.map is None:
                messages.error(request, 'Please upload a % to 22-Scale Map to the Assessment and Try Again!')
                return redirect(reverse('chemapp:student', kwargs={'student_id': student_id, }))

            # Use the Percentage to 22-Scale Mapping
            jsonDec = json.decoder.JSONDecoder()
            mapList = jsonDec.decode(assessment.map)

            finalGrade22Scale = int(mapList[roundedFinalGradePercentage])

            # Convert 22-Scale to the Band
            band = GRADE_TO_BAND[finalGrade22Scale]

            assessmentGrade.finalGrade = finalGrade
            assessmentGrade.finalGradePercentage = roundedFinalGradePercentage
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
                messages.success(request, 'Final Grade Added Successfully!')
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

            # Check if Final Grade is more than the available Assessment Marks
            assessmentMarks = assessment.totalMarks
            if finalGrade > assessmentMarks:
                messages.error(request, 'Final Grade exceeds Available Assessment Marks!')
                return redirect(reverse('chemapp:edit_final_grade',
                                        kwargs={'student_id': student_id, 'course_name_slug': course_name_slug,
                                                'assessment_name_slug': assessment_name_slug}))

            # Convert final grade to Percentage
            finalGradePercentage = (finalGrade * 100) / assessment.totalMarks
            roundedFinalGradePercentage = round(finalGradePercentage)

            # Use the Percentage to 22-Scale Mapping
            jsonDec = json.decoder.JSONDecoder()
            mapList = jsonDec.decode(assessment.map)

            finalGrade22Scale = int(mapList[roundedFinalGradePercentage])

            # Convert 22-Scale to the Band
            band = GRADE_TO_BAND[finalGrade22Scale]

            assessmentGrade.finalGrade = finalGrade
            assessmentGrade.finalGradePercentage = roundedFinalGradePercentage
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
                messages.success(request, 'Final Grade Updated Successfully!')
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
        assessmentGrade.finalGradePercentage = None
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


# Upload Assessment Information Submission/NDP/Good Cause
@login_required
def upload_student_assessment_info_csv(request, course_name_slug, assessment_name_slug):
    course = Course.objects.get(slug=course_name_slug)
    assessment = Assessment.objects.get(slug=assessment_name_slug, course=course)

    uploadAssessmentInfoDict = {}
    uploadAssessmentInfoDict['course_name_slug'] = course_name_slug
    uploadAssessmentInfoDict['assessment_name_slug'] = assessment_name_slug

    if request.method == "GET":
        return render(request, 'chemapp/upload_student_assessment_info_csv.html', context=uploadAssessmentInfoDict)

    csv_file = request.FILES['file']
    if not csv_file.name.endswith('.csv'):
        messages.error(request, 'THIS IS NOT A CSV FILE')
        return redirect(
            reverse('chemapp:upload_student_assessment_info_csv', kwargs={'course_name_slug': course_name_slug,
                                                                          'assessment_name_slug': assessment_name_slug}))

    data_set = csv_file.read().decode('UTF-8')
    io_string = io.StringIO(data_set)
    next(io_string)
    for column in csv.reader(io_string, delimiter=',', quotechar="|"):
        ndp = column[2]
        goodCause = column[3]

        # Converts date string to datetime object
        submissionDateString = column[1]
        submissionDate = datetime.strptime(submissionDateString, '%d/%m/%Y %H:%M')  # Unaware datetime object
        submissionDate = submissionDate.replace(tzinfo=pytz.UTC)  # Aware datetime object

        if ndp == "TRUE":
            ndp = True
        else:
            ndp = False

        if goodCause == "TRUE":
            goodCause = True
        else:
            goodCause = False

        # Check if submission date and time is after due date
        if submissionDate > assessment.dueDate:
            late = True
        else:
            late = False

        # Check if Student Exists
        try:
            student = Student.objects.get(studentID=column[0])
        except Student.DoesNotExist:
            messages.error(request, 'Student with ID number: ' + str(column[0]) + ' does not exist!')
            return redirect(
                reverse('chemapp:upload_student_assessment_info_csv', kwargs={'course_name_slug': course_name_slug,
                                                                              'assessment_name_slug': assessment_name_slug}))

        created = AssessmentGrade.objects.update_or_create(
            student=student,
            assessment=assessment,
            defaults={'submissionDate': submissionDate,
                      'noDetriment': ndp,
                      'goodCause': goodCause,
                      'late': late,
                      }
        )

        components = AssessmentComponent.objects.filter(assessment=assessment)
        for component in components:
            created = AssessmentComponentGrade.objects.update_or_create(
                student=Student.objects.get(studentID=int(column[0])),
                assessmentComponent=component,
                defaults={'grade': None
                          }
            )

    messages.success(request, "Student Assessment Information Added Successfully!")
    return redirect(reverse('chemapp:course', kwargs={'course_name_slug': course_name_slug}))


@login_required
@permission_required_context('chemapp.add_assessmentComponents', 'No permission to add_grades', raise_exception=True)
def upload_grades_csv(request, course_name_slug, assessment_name_slug, assessment_component_slug):
    course = Course.objects.get(slug=course_name_slug)
    assessment = Assessment.objects.get(slug=assessment_name_slug, course=course)
    component = AssessmentComponent.objects.get(slug=assessment_component_slug, assessment=assessment)

    uploadComponentGradesDict = {}
    uploadComponentGradesDict['course_name_slug'] = course_name_slug
    uploadComponentGradesDict['assessment_name_slug'] = assessment_name_slug
    uploadComponentGradesDict['assessment_component_slug'] = assessment_component_slug

    if request.method == "GET":
        return render(request, 'chemapp/upload_grades_csv.html', context=uploadComponentGradesDict)

    csv_file = request.FILES['file']
    if not csv_file.name.endswith('.csv'):
        messages.error(request, 'THIS IS NOT A CSV FILE')
        return redirect(reverse('chemapp:upload_grades_csv', kwargs={'course_name_slug': course_name_slug,
                                                                     'assessment_name_slug': assessment_name_slug,
                                                                     'assessment_component_slug': assessment_component_slug}))

    # Check that Students have been added to the Course
    students = Student.objects.filter(courses__slug=course_name_slug)
    if not students:
        messages.error(request, 'Please Upload Students First and Try Again!')
        return redirect(
            reverse('chemapp:upload_grades_csv', kwargs={'course_name_slug': course_name_slug,
                                                         'assessment_name_slug': assessment_name_slug,
                                                         'assessment_component_slug': assessment_component_slug}))

    # Check that Assessment Student Information has been uploaded
    for student in students:
        try:
            assessmentGrade = AssessmentGrade.objects.get(assessment=assessment, student=student)
        except AssessmentGrade.DoesNotExist:
            messages.error(request, 'Please Upload the Student Assessment Information(NDP/GC/Submission and Try Again!')
            return redirect(
                reverse('chemapp:upload_grades_csv', kwargs={'course_name_slug': course_name_slug,
                                                             'assessment_name_slug': assessment_name_slug,
                                                             'assessment_component_slug': assessment_component_slug}))

    # Check if Map has been uploaded
    if assessment.map is None:
        messages.error(request, 'Please upload a % to 22-Scale Map to the Assessment and Try Again!')
        return redirect(
            reverse('chemapp:upload_grades_csv', kwargs={'course_name_slug': course_name_slug,
                                                         'assessment_name_slug': assessment_name_slug,
                                                         'assessment_component_slug': assessment_component_slug}))

    data_set = csv_file.read().decode('UTF-8')
    io_string = io.StringIO(data_set)
    next(io_string)
    for column in csv.reader(io_string, delimiter=',', quotechar="|"):
        if float(column[1]) > component.marks:
            messages.error(request,
                           'Student with ID number: %s has been awarded a grade higher than %s which is the highest mark available' % (
                               column[0], component.marks))
            return redirect(reverse('chemapp:upload_grades_csv', kwargs={'course_name_slug': course_name_slug,
                                                                         'assessment_name_slug': assessment_name_slug,
                                                                         'assessment_component_slug': assessment_component_slug}))

        created = AssessmentComponentGrade.objects.update_or_create(
            student=Student.objects.get(studentID=int(column[0])),
            assessmentComponent=component,
            defaults={'grade': float(column[1])
                      }
        )

    # Update Assessment Component to show that Grades have been added
    component.gradesAdded = True
    component.save()

    canCourseGradeBeCalculated = True
    canCalculateAssessmentGrades = True

    components = AssessmentComponent.objects.filter(assessment=assessment)
    # Check if its possible to calculate the Assessment Grades
    for component in components:
        if component.gradesAdded is False:
            canCalculateAssessmentGrades = False

    if canCalculateAssessmentGrades is True:
        for student in students:
            assessmentGrade = AssessmentGrade.objects.get(assessment=assessment, student=student)
            for component in components:
                # Check that all required Components have been answered
                if component.required is True:
                    try:
                        componentGrade = AssessmentComponentGrade.objects.get(assessmentComponent=component,
                                                                              student=student)

                    except AssessmentComponentGrade.DoesNotExist:
                        messages.error(request,
                                       'Student with ID number: ' + str(student.studentID) + ' has not answered ' +
                                       str(component.description) + ' which is required')
                        return redirect(
                            reverse('chemapp:upload_grades_csv', kwargs={'course_name_slug': course_name_slug,
                                                                         'assessment_name_slug': assessment_name_slug,
                                                                         'assessment_component_slug': assessment_component_slug}))

            # Calculate Assessment Grade
            count = 0
            grade = 0
            for component in components:
                try:
                    componentGrade = AssessmentComponentGrade.objects.get(assessmentComponent=component,
                                                                          student=student)

                    if componentGrade.grade is not None:
                        count = count + 1
                        grade = grade + componentGrade.grade

                except AssessmentComponentGrade.DoesNotExist:
                    pass

            # Check if the number of components answered match number of components needed
            if count == assessment.componentNumberNeeded:
                componentNumberMatch = True

                # Convert final grade to Percentage
                finalGradePercentage = (grade * 100) / assessment.totalMarks
                roundedFinalGradePercentage = round(finalGradePercentage)

                # Use the Percentage to 22-Scale Mapping
                jsonDec = json.decoder.JSONDecoder()
                mapList = jsonDec.decode(assessment.map)

                finalGrade22Scale = int(mapList[roundedFinalGradePercentage])

                # Convert 22-Scale to the Band
                band = GRADE_TO_BAND[finalGrade22Scale]

                assessmentGrade.markedGrade = grade
                assessmentGrade.finalGrade = grade
                assessmentGrade.finalGradePercentage = roundedFinalGradePercentage
                assessmentGrade.finalGrade22Scale = finalGrade22Scale
                assessmentGrade.band = band
                assessmentGrade.componentNumberAnswered = count
                assessmentGrade.componentNumberMatch = componentNumberMatch
                assessmentGrade.save()

                # Check if its possible to calculate the Course Grade
                assessments = Assessment.objects.filter(course=course)
                assessmentGrades = []
                for assessmentTemp in assessments:
                    try:
                        assessmentGradeObject = AssessmentGrade.objects.get(assessment=assessmentTemp, student=student)

                        if (assessmentGradeObject.finalGrade is None):
                            canCourseGradeBeCalculated = False
                        else:
                            assessmentGrades.append(assessmentGradeObject)

                    except AssessmentGrade.DoesNotExist:
                        canCourseGradeBeCalculated = False

                if canCourseGradeBeCalculated is True:
                    courseGrade = 0
                    for assessmentGrade in assessmentGrades:
                        weight = assessmentGrade.assessment.weight
                        weightedGrade = weight * assessmentGrade.finalGrade22Scale
                        courseGrade = courseGrade + weightedGrade

                    courseGrade = round(courseGrade)
                    band = GRADE_TO_BAND[courseGrade]

                    courseGradeObject = CourseGrade.objects.create(course=course, student=student,
                                                                   grade=courseGrade,
                                                                   band=band)
            else:
                componentNumberMatch = False

                messages.error(request, 'Student with ID number: '
                               + str(student.studentID) + ' has not answered the correct number of components')
                return redirect(
                    reverse('chemapp:upload_grades_csv', kwargs={'course_name_slug': course_name_slug,
                                                                 'assessment_name_slug': assessment_name_slug,
                                                                 'assessment_component_slug': assessment_component_slug}))

        if canCourseGradeBeCalculated is True:
            messages.success(request,
                             'Grades Added Successfully, Assessment Grades Calculated and Course Grades Calculated')
        else:
            messages.success(request, 'Grades Added Successfully and Assessment Grades Calculated')

        return redirect(reverse('chemapp:course', kwargs={'course_name_slug': course_name_slug}))

    else:
        messages.success(request, 'Component Grades Added Successfully!')
        return redirect(reverse('chemapp:course', kwargs={'course_name_slug': course_name_slug}))


@login_required
def staff(request):
    StaffDict = {}
    # checking order by
    staff = Staff.objects.order_by('lastName')
    StaffDict['staff'] = staff

    return render(request, 'chemapp/staff.html', context=StaffDict)


@login_required
def staff_member(request, staffID):
    staff_memberDict = {}
    try:
        staff = Staff.objects.get(staffID=staffID)
        courses = Course.objects.filter(lecturers__staffID=staffID)

        staff_memberDict['courses'] = courses
        staff_memberDict['staff'] = staff
        staff_memberDict['staffID'] = staffID

    except Staff.DoesNotExist:
        raise Http404("Staff member does not exist")

    return render(request, 'chemapp/staff_member.html', context=staff_memberDict)


@login_required
def add_staff(request):
    addStaffDict = {}

    if request.method == 'POST':
        staff_form = StaffForm(request.POST)
        if staff_form.is_valid():
            staffID = staff_form.cleaned_data.get('staffID')
            firstName = staff_form.cleaned_data.get('firstName')
            lastName = staff_form.cleaned_data.get('lastName')
            username = firstName + lastName

            # Check if Staff Member has already been added
            try:
                staff = Staff.objects.get(staffID=staffID)
                messages.error(request, 'Staff Member has already been added!')
                return redirect(reverse('chemapp:add_staff'))
            except Staff.DoesNotExist:
                pass

            staff = staff_form.save()

            # Create User
            user_object = User.objects.create_user(username, password=str(staffID))

            messages.success(request, "Staff Member Added Successfully")
            return redirect(reverse('chemapp:staff_member', kwargs={'staffID': staffID}))
        else:
            print(staff_form.errors)
    else:
        staff_form = StaffForm()

    addStaffDict['staff_form'] = staff_form
    return render(request, 'chemapp/add_staff.html', context=addStaffDict)


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

            messages.success(request, 'Staff Member was updated successfully!')
            return redirect(reverse('chemapp:staff_member', kwargs={'staffID': staffID}))
        else:
            print(edit_staff_form.errors)
    else:
        edit_staff_form = EditStaffForm(instance=staff)

    editStaffDict['edit_staff_form'] = edit_staff_form

    return render(request, 'chemapp/edit_staff.html', context=editStaffDict)


@login_required
def delete_staff(request, staffID):
    staff = Staff.objects.get(staffID=staffID)
    user = User.objects.get(username=staff.username)

    if request.method == 'POST':
        staff.delete()
        user.delete()

        messages.success(request, 'Staff Member deleted successfully!')
        return redirect(reverse('chemapp:staff'))

    return render(request, 'chemapp/staff_member.html', context={})


@login_required
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
