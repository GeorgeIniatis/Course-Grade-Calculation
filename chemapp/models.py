from django.db import models
from django.contrib.auth.models import User
from django.template.defaultfilters import slugify
from django.core.validators import MaxValueValidator, MinValueValidator
from datetime import datetime
from colorfield.fields import ColorField
import hashlib

COURSE_LEVEL_CHOICES = [
    ('1', 'Level 1'),
    ('2', 'Level 2'),
    ('3', 'Honours'),
    ('4', 'Postgraduate'),
]

STUDENT_LEVEL_CHOICES = [
    ('1', 'Level 1'),
    ('2', 'Level 2'),
    ('3', 'Honours Level 3'),
    ('4', 'Honours Level 4'),
    ('5', 'Honours Level 5'),
    ('6', 'Postgraduate'),
]

SEMESTER_CHOICES = [
    ('1', 'Semester 1'),
    ('2', 'Semester 2'),
    ('Both', 'Both'),
]

GRADE_TO_BAND = {22: 'A1', 21: 'A2', 20: 'A3', 19: 'A4', 18: 'A5',
                 17: 'B1', 16: 'B2', 15: 'B3',
                 14: 'C1', 13: 'C2', 12: 'C3',
                 11: 'D1', 10: 'D2', 9: 'D3',
                 8: 'E1', 7: 'E2', 6: 'E3',
                 5: 'F1', 4: 'F2', 3: 'F3',
                 2: 'G1', 1: 'G2', 0: 'H',
                 }

BAND_TO_GRADE = {'A1': 22, 'A2': 21, 'A3': 20, 'A4': 19, 'A5': 18,
                 'B1': 17, 'B2': 16, 'B3': 15,
                 'C1': 14, 'C2': 13, 'C3': 12,
                 'D1': 11, 'D2': 10, 'D3': 9,
                 'E1': 8, 'E2': 7, 'E3': 6,
                 'F1': 5, 'F2': 4, 'F3': 3,
                 'G1': 2, 'G2': 1, 'H': 0,
                 }

STAFF_TITTLES = [
    ('Prof', 'Prof'),
    ('Dr', 'Dr'),
    ('Mr', 'Mr'),
    ('Miss', 'Miss'),
    ('Mrs', 'Mrs'),
]


class Degree(models.Model):
    degreeCode = models.CharField(max_length=30,
                                  unique=True,
                                  help_text='eg.4H-CMC')

    name = models.CharField(max_length=200)

    numberOfCourses = models.PositiveIntegerField(default=0,
                                                  verbose_name="Number of Courses")

    numberOfStudents = models.PositiveIntegerField(default=0,
                                                   verbose_name="Number of Students")

    slug = models.SlugField(unique=True)

    def save(self, *args, **kwargs):
        self.degreeCode = self.degreeCode.upper()
        self.slug = slugify(self.degreeCode)
        super(Degree, self).save(*args, **kwargs)

    def __str__(self):
        return self.degreeCode


class Staff(models.Model):
    staffID = models.PositiveIntegerField(validators=[MaxValueValidator(9999999)],
                                          unique=True,
                                          verbose_name="Staff ID")

    title = models.CharField(max_length=20,
                             verbose_name="Title",
                             choices=STAFF_TITTLES)

    firstName = models.CharField(max_length=128,
                                 verbose_name="First Name")

    lastName = models.CharField(max_length=128,
                                verbose_name="Last Name")

    username = models.CharField(max_length=128)

    comments = models.TextField(max_length=2000,
                                blank=True,
                                help_text='Anything worth mentioning')

    class Meta:
        verbose_name_plural = 'Staff'

    def save(self, *args, **kwargs):
        self.username = (self.firstName + self.lastName)
        super(Staff, self).save(*args, **kwargs)

    def __str__(self):
        return (str(self.title) + " " + str(self.firstName) + " " + str(self.lastName))


class Course(models.Model):
    code = models.CharField(max_length=30,
                            help_text='eg. CHEM1005')

    degree = models.ForeignKey(Degree,
                               on_delete=models.CASCADE)

    creditsWorth = models.IntegerField(validators=[MaxValueValidator(120), MinValueValidator(5)],
                                       verbose_name='Credits Worth',
                                       help_text='5-120 Credits')

    name = models.CharField(max_length=200,
                            help_text='eg.Biological Chemistry 3')

    shortHand = models.CharField(max_length=30,
                                 help_text='eg.BIOCHEM3')

    level = models.CharField(max_length=20,
                             choices=COURSE_LEVEL_CHOICES)

    academicYearTaught = models.CharField(max_length=5,
                                          verbose_name="Academic Year Taught",
                                          help_text='eg.19-20')

    semester = models.CharField(max_length=20,
                                choices=SEMESTER_CHOICES)

    description = models.TextField(max_length=2000)

    comments = models.TextField(max_length=2000,
                                blank=True,
                                help_text='Anything worth mentioning')

    minimumPassGrade = models.CharField(max_length=2,
                                        verbose_name="Minimum Pass Grade",
                                        help_text='eg.B3')

    minimumPassGrade22Scale = models.PositiveIntegerField()

    minimumRequirementsForCredit = models.DecimalField(max_digits=3,
                                                       decimal_places=2,
                                                       verbose_name="Minimum Requirements For Credit",
                                                       help_text='eg.0.60')

    numberOfStudents = models.PositiveIntegerField(default=0,
                                                   verbose_name="Number of Students")

    lecturers = models.ManyToManyField(Staff, verbose_name="Course Lecturers")

    slug = models.SlugField(unique=True)

    courseColor = ColorField(default='#FF0000')

    class Meta:
        unique_together = ('code', 'degree')

    def save(self, *args, **kwargs):
        self.code = self.code.upper()
        self.shortHand = self.shortHand.upper()
        self.minimumPassGrade = self.minimumPassGrade.upper()
        self.minimumPassGrade22Scale = BAND_TO_GRADE[self.minimumPassGrade]
        self.slug = slugify(str(self.code) + "-" + str(self.degree))
        super(Course, self).save(*args, **kwargs)

    def __str__(self):
        return (str(self.name) + " (" + str(self.degree) + ")")


class Student(models.Model):
    studentID = models.PositiveIntegerField(validators=[MaxValueValidator(9999999)],
                                            unique=True,
                                            verbose_name="Student ID")

    anonID = models.CharField(max_length=128,
                                    unique=True,
                                    verbose_name="Anonymous ID")

    firstName = models.CharField(max_length=128,
                                 verbose_name="First Name")

    lastName = models.CharField(max_length=128,
                                verbose_name="Last Name")

    # Degree
    academicPlan = models.ForeignKey(Degree,
                                     on_delete=models.CASCADE,
                                     verbose_name="Academic Plan/Degree")

    level = models.CharField(max_length=20,
                             choices=STUDENT_LEVEL_CHOICES)

    graduationDate = models.DateField(blank=True,
                                      verbose_name="Graduation Date")

    comments = models.TextField(max_length=2000,
                                blank=True)

    gapYear = models.BooleanField(default=False)

    status = models.CharField(max_length=20)

    courses = models.ManyToManyField(Course, blank=True)

    def save(self, *args, **kwargs):
        self.anonID = hashlib.sha1(str(self.studentID).encode('UTF-8')).hexdigest()[:10]
        self.status = 'Enrolled' if self.gapYear is False else 'Gap Year'
        super(Student, self).save(*args, **kwargs)

    def __str__(self):
        return (str(self.firstName) + " " + str(self.lastName) + " " + str(self.studentID))


class CourseGrade(models.Model):
    grade = models.PositiveIntegerField()

    band = models.CharField(max_length=2)

    course = models.ForeignKey(Course,
                               on_delete=models.CASCADE)

    student = models.ForeignKey(Student,
                                on_delete=models.CASCADE)

    class Meta:
        unique_together = ('course', 'student')

    def save(self, *args, **kwargs):
        self.band = GRADE_TO_BAND[round(self.grade)]
        super(CourseGrade, self).save(*args, **kwargs)

    def __str__(self):
        return (str(self.course) + " " + str(self.student))


class Assessment(models.Model):
    weight = models.DecimalField(max_digits=6,
                                 decimal_places=5,
                                 help_text='eg.0.50')

    totalMarks = models.PositiveIntegerField(verbose_name="Total Marks",
                                             help_text="eg.50")

    assessmentName = models.CharField(max_length=200,
                                      help_text='eg.Lab 1',
                                      verbose_name='Assessment Name')

    dueDate = models.DateTimeField(verbose_name="Due Date and Time",
                                   help_text='eg.11/10/2021 at 0800')

    course = models.ForeignKey(Course,
                               on_delete=models.CASCADE)

    slug = models.SlugField()

    # Example
    # If an exam has 3 required question and the student needs to answer 1 more from 4 optional questions
    # the componentNumberNeeded would be 4 in this case
    componentNumberNeeded = models.PositiveIntegerField(verbose_name="Component Number Needed",
                                                        help_text="Includes required and optional components",
                                                        default=0)

    map = models.TextField(verbose_name="22 Scale Map",
                           null=True,
                           blank=True)

    class Meta:
        unique_together = ('assessmentName', 'course')

    def save(self, *args, **kwargs):
        self.slug = slugify(self.assessmentName)
        super(Assessment, self).save(*args, **kwargs)

    def __str__(self):
        return (str(self.course) + " " + str(self.assessmentName))


class AssessmentGrade(models.Model):
    submissionDate = models.DateTimeField(verbose_name="Submission Date and Time")

    noDetriment = models.BooleanField(default=False,
                                      verbose_name="No Detriment Policy")

    goodCause = models.BooleanField(default=False,
                                    verbose_name="Good Cause")

    markedGrade = models.DecimalField(max_digits=5,
                                      decimal_places=2,
                                      verbose_name="Marked Grade",
                                      null=True,
                                      blank=True)

    finalGrade = models.DecimalField(max_digits=5,
                                     decimal_places=2,
                                     null=True,
                                     blank=True,
                                     verbose_name="Final Grade")

    finalGradePercentage = models.PositiveIntegerField(verbose_name= "Final Grade Percentage",
                                                       null=True,
                                                       blank=True)

    finalGrade22Scale = models.PositiveIntegerField(verbose_name="Final Grade Out of 22",
                                                    null=True,
                                                    blank=True)

    band = models.CharField(max_length=2,
                            null=True,
                            blank=True)

    componentNumberAnswered = models.PositiveIntegerField(verbose_name="Component Number Answered",
                                                          help_text="Includes required and optional components",
                                                          default=0)

    late = models.BooleanField(default=False,
                               verbose_name="Late")

    componentNumberMatch = models.BooleanField(default=False,
                                               verbose_name="Component Numbers Match")

    assessment = models.ForeignKey(Assessment,
                                   on_delete=models.CASCADE)

    student = models.ForeignKey(Student,
                                on_delete=models.CASCADE)

    class Meta:
        unique_together = ('assessment', 'student')

    def __str__(self):
        return (str(self.assessment) + " " + str(self.student))


class AssessmentComponent(models.Model):
    required = models.BooleanField(default=False)

    status = models.CharField(max_length=20)

    marks = models.PositiveIntegerField()

    description = models.CharField(max_length=100)

    lecturer = models.ForeignKey(Staff,
                                 on_delete=models.CASCADE)

    assessment = models.ForeignKey(Assessment,
                                   on_delete=models.CASCADE)

    slug = models.SlugField()

    gradesAdded = models.BooleanField(default=False)

    class Meta:
        unique_together = ('description', 'assessment')

    def save(self, *args, **kwargs):
        self.status = 'Required' if self.required is True else 'Optional'
        self.slug = slugify(self.description)
        super(AssessmentComponent, self).save(*args, **kwargs)

    def __str__(self):
        return (str(self.assessment) + " " + str(self.description))


class AssessmentComponentGrade(models.Model):
    grade = models.DecimalField(max_digits=5,
                                decimal_places=2,
                                null=True,
                                blank=True)

    assessmentComponent = models.ForeignKey(AssessmentComponent,
                                            on_delete=models.CASCADE,
                                            verbose_name="Assessment Component")

    student = models.ForeignKey(Student,
                                on_delete=models.CASCADE)

    class Meta:
        unique_together = ('assessmentComponent', 'student')

    def __str__(self):
        return (str(self.assessmentComponent) + " " + str(self.student))
