from django import forms
from chemapp.models import *
from django.contrib.auth.models import User

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

        
