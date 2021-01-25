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

    degree = forms.ModelChoiceField(label='',
                                    empty_label="Degree",
                                    queryset=Degree.objects.all(),
                                    widget=forms.Select(
                                        attrs={
                                            'style':'width:300px',
                                            }
                                        ))               
    class Meta:
        model = Course
        fields = {'code','degree','creditsWorth','name','shortHand','year','academicYearTaught',
                  'semester','description','comments','minimumPassGrade',
                  'minimumRequirementsForCredit'}

class AssessmentForm(forms.ModelForm):
    assessmentName = forms.CharField(label='',
                                     widget = forms.TextInput(
                                         attrs={
                                             'maxlength':'200',
                                             'type':'text',
                                             'placeholder':'Name',
                                             'style':'width:300px',
                                             'required':True,
                                            }
                                         ))
    
    weight = forms.DecimalField(label='',
                                widget = forms.NumberInput(
                                    attrs={
                                        'min':'0',
                                        'max':'1',
                                        'step':'0.05',
                                        'type':'number',
                                        'placeholder':'Weight',
                                        'style': 'width:300px',
                                        'required':True,
                                        }
                                    ))
    dueDate = forms.DateTimeField(input_formats=['%Y-%m-%dT%H:%M',],
                                  label='',
                                  widget = forms.DateTimeInput(
                                      attrs={
                                          'type':'datetime-local',
                                          'style':'width:300px',
                                          'required':True,
                                          },
                                      format='%Y-%m-%dT%H:%M'))

    totalMarks = forms.IntegerField(label='',
                                    widget =  forms.NumberInput(
                                        attrs={
                                            'min':'0',
                                            'type':'number',
                                            'placeholder':'Total Marks',
                                            'style': 'width:300px',
                                            'required':True,
                                            }
                                        ))
                                    
    field_order = ['assessmentName', 'weight','totalMarks', 'dueDate']

    class Meta:
        model = Assessment
        fields = {'assessmentName','weight','totalMarks','dueDate'}

class AssessmentComponentForm(forms.ModelForm):
    required = forms.BooleanField(label='Required',
                                  required = False,
                                  widget = forms.CheckboxInput(
                                      attrs={
                                          'placeholder':'Required',
                                          }
                                      ))

    marks = forms.IntegerField(label='',
                               widget = forms.NumberInput(
                                   attrs={
                                        'min':'0',
                                        'type':'number',
                                        'placeholder':'Marks',
                                        'style': 'width:300px',
                                        'required':True,
                                        }
                                    ))
    description = forms.CharField(label='',
                                  widget = forms.TextInput(
                                      attrs={
                                          'maxlength':'100',
                                          'type':'text',
                                          'placeholder':'Description',
                                          'style':'width:300px',
                                          'required':True,
                                          }
                                      ))
    
    field_order = ['required', 'description', 'marks']

    class Meta:
        model = AssessmentComponent
        fields = {'required','marks','description'}
                            
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
