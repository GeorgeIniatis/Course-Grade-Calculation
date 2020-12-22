from django.db import models
from django.contrib.auth.models import User
from django.template.defaultfilters import slugify
from django.core.validators import MaxValueValidator, MinValueValidator

# Need to be modified or removed
class Category(models.Model):
    name = models.CharField(max_length=128, unique=True)
    slug = models.SlugField(unique=True)
    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super(Category, self).save(*args, **kwargs)
    class Meta:
        verbose_name_plural = 'Categories'
    def __str__(self):
        return self.name

class Page(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    title = models.CharField(max_length=128)
    url = models.URLField()
    views = models.IntegerField(default=0)
    def __str__(self):
        return self.title

#People that have access to the site
#Lecturers etc
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    #Not really needed
    date_of_birth = models.DateField
    profile_image = models.ImageField(upload_to='profile_images', blank=True)

    class Meta:
        verbose_name_plural = 'Users'
        
    def __str__(self):
        return self.user.username

class Course(models.Model):
    #I dont know the format of course codes need to check, format, max length ect
    courseCode = models.CharField(max_length=128, unique=True)
    #any paramets here max min?
    #Question to ask customer 
    courseCredits = models.IntegerField(validators=[MaxValueValidator(20), MinValueValidator(5)])

    courseName = models.CharField(max_length=200)
    courseShortHand = models.CharField(max_length=50)
    #could be Integer? same problem as currentYear in Student model
    #Changed them both to integers
    courseYear = models.IntegerField(validators=[MaxValueValidator(5), MinValueValidator(1)])
    #I think they want as well a field that would show the current year that the course is being taught
    #2019-2020 something like that
    academicYearTaught = models.CharField(max_length=50)
    semester = models.IntegerField(validators=[MaxValueValidator(2), MinValueValidator(1)])

    #description could possible be an uploaded txt file so we dont have to manage length.
    description = models.TextField(max_length = 2000)
    comments = models.TextField(max_length=500, blank=True)
    #may have to change decimal places
    minimumPassGrade = models.CharField(max_length=2)
    #Percentage of assessments that need to be submitted in order to get credits
    #eg 0.75
    minimumRequirementsForCredit = models.DecimalField(max_digits=3, decimal_places = 2)


    #courseGrade = models.OneToOneField('CourseGrade', on_delete=models.CASCADE, primary_key=True)

    #assessments = models.ManyToManyField(Assessment)

    def __str__(self):
        return self.courseCode

class Student(models.Model):
    firstName = models.CharField(max_length=128)
    lastName = models.CharField(max_length=128)
    #not quite sure why we need this?
    #This will be the name provided in the excel file as far as i know
    #Something like John,Smith with the comma included
    myCampusName = models.CharField(max_length=128)
    studentID = models.CharField(max_length=7,unique=True)
    anonID = models.CharField(max_length=7,unique=True)
    academicPlan = models.CharField(max_length=128)

    #should we change this to restricted choice? integer field?
    currentYear = models.IntegerField(validators=[MaxValueValidator(5), MinValueValidator(1)])
    
    graduationDate = models.DateTimeField(null=True, blank=True)
    comments = models.TextField(max_length=500, blank=True)
    #I don't really think gap year is necessary as they could start uni at any age.
    #gapYear = models.BooleanField(default = False)
    courses = models.ManyToManyField(Course)

    #courseGrades

    def __str__(self):
        return self.anonID

class CourseGrade(models.Model):
     grade = models.DecimalField(max_digits=5,decimal_places=2)
     course = models.OneToOneField(Course, on_delete=models.CASCADE)
     student = models.ForeignKey(Student, on_delete=models.CASCADE)

     def __str__(self):
        return (str(self.course) + " - " + str(self.student))


# class Assesment(models.Model):
#     weight = models.DecimlField(max_digits=5,decimal_places=2)
#     name = models.CharField(max_length=128)
#     dueDate = models.DateTimeField(null=True, blank=True)
#     assessmentComps = ######### need other model
#
#
#
#
#
# class AssessmentGrade(models.Model):
#     #basic restricted choice options
#     LATE_STATUS = (
#         ('1', '1 Band'),
#         ('2', '2 Bands'),
#     )
#
#     GOOD_CAUSE_ACTION = (
#         ('resit', 'resit exam'),
#         ('ca', 'credit awarded'),
#     )
#
#     submissionDate = models.DateTimeField(null=True, blank=True)
#     lateStatus = models.CharField(choices = LATE_STATUS, blank = True)
#     noDetriment = models.BooleanField(default = False)
#     goodCause = models.BooleanField(default = False)
#     goodCauseAction = models.CharField(choices = GOOD_CAUSE_ACTION, blank = True)
#     markedGrade = models.DecimlField(max_digits=5,decimal_places=2)
#     # Is there any need for the penalty field?
#     #penalty = models.CharField()
#     finalGrade = models.DecimlField(max_digits=5,decimal_places=2)
#     #assessmentCompGrades = ############# no clue what this is
#
#
# class AssessmentComponents(models.Model):
#     required = models.BooleanField(default = False)
#     weight = models.DecimlField(max_digits=5,decimal_places=2)
#     description = models.CharField(max_length=100)
#
# class AssessmentComponentGrade(models.Model):
#     grade = models.DecimalField(max_digits=5,decimal_places=2)
