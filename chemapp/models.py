from django.db import models
from django.contrib.auth.models import User
from django.template.defaultfilters import slugify
from django.core.validators import MaxValueValidator, MinValueValidator

#People that have access to the site
#Lecturers etc
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=128)

    class Meta:
        verbose_name_plural = 'Users'
        
    def __str__(self):
        return self.user.username

class Course(models.Model):
    #I dont know the format of course codes need to check, format, max length ect
    code = models.CharField(max_length=128, unique=True)
    
    #any paramets here max min?
    #Question to ask customer 
    creditsWorth = models.IntegerField(validators=[MaxValueValidator(20), MinValueValidator(5)],verbose_name="Credits Worth")

    name = models.CharField(max_length=200)
    shortHand = models.CharField(max_length=50)
    
    #could be Integer? same problem as currentYear in Student model
    #Changed them both to integers
    year = models.IntegerField(validators=[MaxValueValidator(5), MinValueValidator(1)])
    
    #I think they want as well a field that would show the current year that the course is being taught
    #2019-2020 something like that
    academicYearTaught = models.CharField(max_length=50, verbose_name="Academic Year Taught")
    
    semester = models.IntegerField(validators=[MaxValueValidator(2), MinValueValidator(1)])

    #description could possible be an uploaded txt file so we dont have to manage length.
    description = models.TextField(max_length = 2000)
    
    comments = models.TextField(max_length=500, blank=True)
    
    #may have to change decimal places
    minimumPassGrade = models.CharField(max_length=2,verbose_name="Minimum Pass Grade")
    
    #Percentage of assessments that need to be submitted in order to get credits
    #eg 0.75
    minimumRequirementsForCredit = models.DecimalField(max_digits=3, decimal_places = 2, verbose_name="Minimum Requirements For Credit")

    slug = models.SlugField(unique=True)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.shortHand)
        super(Course, self).save(*args, **kwargs)
    
    def __str__(self):
        return self.shortHand
    
class Student(models.Model):
    firstName = models.CharField(max_length=128,verbose_name="First Name")
    lastName = models.CharField(max_length=128,verbose_name="Last Name")
    #not quite sure why we need this?
    #This will be the name provided in the excel file as far as i know
    #Something like John,Smith with the comma included
    myCampusName = models.CharField(max_length=128, verbose_name="myCampus Name")
    
    studentID = models.PositiveIntegerField(validators=[MaxValueValidator(9999999)],unique=True, verbose_name="Student ID")
    anonID = models.PositiveIntegerField(validators=[MaxValueValidator(9999999)],unique=True, verbose_name="Anonymous ID")
    
    academicPlan = models.CharField(max_length=128,verbose_name="Academic Plan")

    #should we change this to restricted choice? integer field?
    currentYear = models.IntegerField(validators=[MaxValueValidator(5), MinValueValidator(1)], verbose_name="Current Year")
    
    graduationDate = models.DateField(null=True, blank=True,verbose_name="Graduation Date")
    comments = models.TextField(max_length=500, blank=True)
    #I don't really think gap year is necessary as they could start uni at any age.
    #gapYear = models.BooleanField(default = False)
    courses = models.ManyToManyField(Course)

    #courseGrades

    def __str__(self):
        return str(self.anonID)

class CourseGrade(models.Model):
     grade = models.DecimalField(max_digits=5,decimal_places=2)
     course = models.ForeignKey(Course, on_delete=models.CASCADE)
     student = models.ForeignKey(Student, on_delete=models.CASCADE)

     class Meta:
         unique_together = ('course', 'student')

     def __str__(self):
        return (str(self.course) + " - " + str(self.student))


class Assessment(models.Model):
     weight = models.DecimalField(max_digits=3,decimal_places=2)
     name = models.CharField(max_length=128)
     dueDate = models.DateTimeField(null=True, blank=True, verbose_name="Due Date and Time")
     course = models.ForeignKey(Course, on_delete=models.CASCADE)

     def __str__(self):
        return (str(self.course) + " - " + str(self.name))
     
class AssessmentGrade(models.Model):
     #basic restricted choice options
     LATE_STATUS = (
         ('1', '1 Band'),
         ('2', '2 Bands'),
     )

     GOOD_CAUSE_ACTION = (
         ('Resit', 'Resit Exam'),
         ('CA', 'Credit Awarded'),
     )

     submissionDate = models.DateTimeField(null=True, blank=True, verbose_name="Submission Date and Time")
     lateStatus = models.CharField(max_length=1,choices = LATE_STATUS, blank = True,verbose_name="Late Status")
     noDetriment = models.BooleanField(default = False,verbose_name="No Detriment Policy")
     goodCause = models.BooleanField(default = False,verbose_name="Good Cause")
     goodCauseAction = models.CharField(max_length=5,choices = GOOD_CAUSE_ACTION, blank = True,verbose_name="Good Cause Action")
     markedGrade = models.DecimalField(max_digits=5,decimal_places=2,verbose_name="Marked Grade")
     # Is there any need for the penalty field?
     #penalty = models.CharField()
     finalGrade = models.DecimalField(max_digits=5,decimal_places=2,verbose_name="Final Grade")
     #assessmentCompGrades = ############# no clue what this is

     assessment = models.ForeignKey(Assessment, on_delete=models.CASCADE)
     student = models.ForeignKey(Student, on_delete=models.CASCADE)

     class Meta:
         unique_together = ('assessment', 'student')

     def __str__(self):
        return (str(self.assessment) + " - " + str(self.student))
     
class AssessmentComponent(models.Model):
     required = models.BooleanField(default = False)
     weight = models.DecimalField(max_digits=3,decimal_places=2)
     marks = models.PositiveIntegerField()
     description = models.CharField(max_length=100)

     assessment = models.ForeignKey(Assessment, on_delete=models.CASCADE)

     def __str__(self):
        return (str(self.assessment) + " - " + str(self.description))
     
class AssessmentComponentGrade(models.Model):
    grade = models.DecimalField(max_digits=5,decimal_places=2)

    assessmentComponent = models.ForeignKey(AssessmentComponent, on_delete=models.CASCADE,verbose_name="Assessment Component")
    student = models.ForeignKey(Student, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('assessmentComponent', 'student')
    
    def __str__(self):
        return (str(self.assessmentComponent) + " - " + str(self.student))
     

     
