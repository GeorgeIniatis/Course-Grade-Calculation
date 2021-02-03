from django.db import models
from django.contrib.auth.models import User
from django.template.defaultfilters import slugify
from django.core.validators import MaxValueValidator, MinValueValidator
from datetime import datetime
from colorfield.fields import ColorField

LEVEL_CHOICES = [
    ('1', 'Level 1'),
    ('2', 'Level 2'),
    ('3', 'Level 3'),
    ('3-M', 'Level 3 MSci'),
    ('3-CS', 'Level 3 Chemical Studies'),
    ('4-M', 'Level 4 MSci'),
    ('4-H-CHEM', 'Level 4 Variation 1'),
    ('4-H-CMC', 'Level 4 Variation 2'),
    ('4-H-C&M', 'Level 4 Variation 3'),
    ('5-M', 'Level 5 Variation 1'),
    ('5-M-CHEM', 'Level 5 Variation 2'),
    ('5-M-CMC', 'Level 5 Variation 3'),
    ('5-M-C&M', 'Level 5 Variation 4'),
    ('5-M-CP', 'Level 5 Variation 5'),
    ]

COLOR_CHOICES = [
    ("#FFFFFF", "white"),
    ("#000000", "black"),
    ]

#Could be removed if not necessary
LATE_STATUS = (
    ('1', '1 Band'),
    ('2', '2 Bands'),
    )

GOOD_CAUSE_ACTION = (
    ('Resit', 'Resit Exam'),
    ('CA', 'Credit Awarded'),
    )

#People that have access to the site
#Lecturers etc
class UserProfile(models.Model):
    user = models.OneToOneField(User,
                                on_delete=models.CASCADE)
    
    title = models.CharField(max_length=128)

    class Meta:
        verbose_name_plural = 'Users'

    def __str__(self):
        return self.user.username

class Degree(models.Model):
    #Input mask?
    degreeCode = models.CharField(max_length=30,
                                  unique=True,
                                  help_text='eg.4H-CMC')

    numberOfCourses = models.PositiveIntegerField(default=0,
                                                  verbose_name="Number of Courses")
    
    numberOfStudents = models.PositiveIntegerField(default=0,
                                                   verbose_name="Number of Students")
    
    def __str__(self):
        return self.degreeCode

class Course(models.Model):
    #I dont know the format of course codes need to check, format, max length ect
    #Input mask?
    code = models.CharField(max_length=30,
                            help_text='eg. CHEM1005')

    degree = models.ForeignKey(Degree,
                               on_delete=models.CASCADE)

    #any paramets here max min?
    #Question to ask customer
    creditsWorth = models.IntegerField(validators=[MaxValueValidator(20), MinValueValidator(5)],
                                       verbose_name='Credits Worth',
                                       help_text='5-20 Credits')

    name = models.CharField(max_length=200,
                            help_text='eg.Biological Chemistry 3')

    shortHand = models.CharField(max_length=30,
                                 help_text='eg.BIOCHEM3')
 
    level = models.CharField(max_length = 20,
                             choices=LEVEL_CHOICES)

    year = models.PositiveIntegerField()
    
    #Input mask?
    academicYearTaught = models.CharField(max_length=5,
                                          verbose_name="Academic Year Taught",
                                          help_text='eg.19-20')

    semester = models.IntegerField(validators=[MaxValueValidator(2), MinValueValidator(1)],
                                   help_text='1-2')

    #description could possible be an uploaded txt file so we dont have to manage length.
    description = models.TextField(max_length=2000)

    comments = models.TextField(max_length=2000,
                                blank=True,
                                help_text='Anything worth mentioning')

    #may have to change decimal places
    minimumPassGrade = models.CharField(max_length=2,
                                        verbose_name="Minimum Pass Grade",
                                        help_text='eg.B3')

    #Percentage of assessments that need to be submitted in order to get credits
    #eg 0.75
    minimumRequirementsForCredit = models.DecimalField(max_digits=3,
                                                       decimal_places = 2,
                                                       verbose_name="Minimum Requirements For Credit",
                                                       help_text='eg.0.60')

    slug = models.SlugField(unique=True)

    COLOR_CHOICES = [
        ("#FFFFFF", "white"),
        ("#000000", "black")
    ]

    courseColor = ColorField(default='#FF0000')

    class Meta:
         unique_together = ('code', 'degree')

    def save(self, *args, **kwargs):
        self.code = self.code.upper()
        self.shortHand = self.shortHand.upper()
        self.minimumPassGrade = self.minimumPassGrade.upper()
        self.year = int(self.level[0])
        self.slug = slugify(str(self.code)+"-"+str(self.degree))
        super(Course, self).save(*args, **kwargs)

    def __str__(self):
        return (str(self.shortHand) + " " + str(self.degree))

class Student(models.Model):
    studentID = models.PositiveIntegerField(validators=[MaxValueValidator(9999999)],
                                            unique=True,
                                            verbose_name="Student ID")
    
    anonID = models.PositiveIntegerField(validators=[MaxValueValidator(9999999)],
                                         unique=True,
                                         verbose_name="Anonymous ID")
    
    firstName = models.CharField(max_length=128,
                                 verbose_name="First Name")
    
    lastName = models.CharField(max_length=128,
                                verbose_name="Last Name")
    
    #not quite sure why we need this?
    #This will be the name provided in the excel file as far as i know
    #Something like John,Smith with the comma included
    #myCampusName = models.CharField(max_length=128, verbose_name="myCampus Name")

    #Degree
    academicPlan = models.ForeignKey(Degree,
                                     on_delete=models.CASCADE,
                                     verbose_name="Academic Plan/Degree")
    
    level = models.CharField(max_length = 20,
                             choices=LEVEL_CHOICES)

    graduationDate = models.DateField(blank=True,
                                      verbose_name="Graduation Date")
    
    comments = models.TextField(max_length=2000,
                                blank=True)
    
    #I don't really think gap year is necessary as they could start uni at any age.
    gapYear = models.BooleanField(default = False)
    
    courses = models.ManyToManyField(Course,blank=True)

    def __str__(self):
        return (str(self.firstName) + " " + str(self.lastName) + " " + str(self.studentID))

class CourseGrade(models.Model):
     grade = models.DecimalField(max_digits=5,
                                 decimal_places=2)
     
     course = models.ForeignKey(Course,
                                on_delete=models.CASCADE)
     
     student = models.ForeignKey(Student,
                                 on_delete=models.CASCADE)

     class Meta:
         unique_together = ('course', 'student')

     def __str__(self):
        return (str(self.course) + " " + str(self.student))


class Assessment(models.Model):
    weight = models.DecimalField(max_digits=3,
                                 decimal_places=2,
                                 help_text='eg.0.50')

    totalMarks = models.PositiveIntegerField(verbose_name= "Total Marks",
                                             help_text= "eg.50")

    assessmentName = models.CharField(max_length=200,
                                      help_text='eg.Lab 1',
                                      verbose_name='Assessment Name')

    dueDate = models.DateTimeField(verbose_name="Due Date and Time",
                                   help_text='eg.11/10/2021 at 0800')

    course = models.ForeignKey(Course,
                               on_delete=models.CASCADE)

    slug = models.SlugField()

    componentsAdded = models.BooleanField(default = False)

    #Example
    #If an exam has 3 required question and the student needs to answer 1 more from 4 optional questions
    #the componentNumberNeeded would be 4 in this case
    componentNumberNeeded = models.PositiveIntegerField(verbose_name= "Component Number Needed",
                                                        help_text= "Includes required and optional components",
                                                        default = 0)

    class Meta:
        unique_together = ('assessmentName', 'course')

    def save(self, *args, **kwargs):
        self.slug = slugify(self.assessmentName)
        super(Assessment, self).save(*args, **kwargs)

    def __str__(self):
        return (str(self.course) + " " + str(self.assessmentName))

class AssessmentGrade(models.Model):
     
     #Removed for now
     #lateStatus = models.CharField(max_length=1,choices = LATE_STATUS,blank = True,verbose_name="Late Status")
     #goodCauseAction = models.CharField(max_length=5,choices = GOOD_CAUSE_ACTION,blank = True,verbose_name="Good Cause Action")
     #penalty = models.CharField()

     submissionDate = models.DateTimeField(verbose_name="Submission Date and Time")
     
     noDetriment = models.BooleanField(default = False,
                                       verbose_name="No Detriment Policy")
     
     goodCause = models.BooleanField(default = False,
                                     verbose_name="Good Cause")
     
     markedGrade = models.DecimalField(max_digits=5,
                                       decimal_places=2,
                                       null=True,
                                       blank=True,
                                       verbose_name="Marked Grade")
     
     finalGrade = models.DecimalField(max_digits=5,
                                      decimal_places=2,
                                      null=True,
                                      blank=True,
                                      verbose_name="Final Grade")

     assessment = models.ForeignKey(Assessment,
                                    on_delete=models.CASCADE)
     
     student = models.ForeignKey(Student,
                                 on_delete=models.CASCADE)

     class Meta:
         unique_together = ('assessment', 'student')

     def __str__(self):
        return (str(self.assessment) + " " + str(self.student))

class AssessmentComponent(models.Model):
    required = models.BooleanField(default = False)

    status = models.CharField(max_length=20)

    marks = models.PositiveIntegerField()

    description = models.CharField(max_length=100)

    assessment = models.ForeignKey(Assessment,
                                   on_delete=models.CASCADE)

    class Meta:
        unique_together = ('description','assessment')

    def save(self, *args, **kwargs):
        self.status = 'Required' if self.required == True  else 'Optional'
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
