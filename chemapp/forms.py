from django import forms
from chemapp.models import *
from django.contrib.auth.models import User
from tempus_dominus.widgets import DatePicker
class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())

    class Meta:
        model = User
        fields = {'username', 'password',}

class UserProfileForm(forms.ModelForm):

    class Meta:
        model = UserProfile
        fields = {'title'}

class CourseForm(forms.ModelForm):

    class Meta:
        model = Course
        fields = ('code','creditsWorth','name','shortHand','year','academicYearTaught',
                  'semester','description','comments','minimumPassGrade',
                  'minimumRequirementsForCredit')

class AssessmentForm(forms.ModelForm):
    dueDate = forms.DateTimeField(input_formats=['%Y-%m-%dT%H:%M',])
    class Meta:
        model = Assessment
        fields = ('weight','assessmentName','dueDate','course')
        exclude = ['course']

class StudentForm(forms.ModelForm):
	class Meta:
		model = Student
		attrs = {'firstName': 'paleblue'}
		fields = ('studentID','firstName','lastName','myCampusName','academicPlan','anonID','graduationDate','currentYear','comments')
		widgets = {
            'graduationDate': DatePicker(
                options={
                    'format': 'DD/MM/YYYY'
                },
                attrs={
                    'prepend': 'fa fa-calendar',
                },
            )
        }

	