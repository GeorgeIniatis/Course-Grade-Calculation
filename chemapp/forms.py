from django import forms
from chemapp.models import *
from django.contrib.auth.models import User
from tempus_dominus.widgets import DatePicker

LEVEL_CHOICES = [
    ('', 'Level'),
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
                                    required = True,
                                    empty_label="Degree",
                                    queryset=Degree.objects.all(),
                                    widget=forms.Select(
                                        attrs={
                                            'style':'width:300px',
                                            }
                                        ))

    level = forms.ChoiceField(label='',
                              required = True,
                              choices=LEVEL_CHOICES,
                              widget=forms.Select(
                                  attrs={
                                      'style':'width:300px',
                                      }
                                  ))
    
    class Meta:
        model = Course
        fields = {'code','degree','creditsWorth','name','shortHand','level','academicYearTaught',
                  'semester','description','comments','minimumPassGrade',
                  'minimumRequirementsForCredit'}

class AssessmentForm(forms.ModelForm):
    assessmentName = forms.CharField(label='',
                                     required = True,
                                     widget = forms.TextInput(
                                         attrs={
                                             'maxlength':'200',
                                             'type':'text',
                                             'placeholder':'Name',
                                             'style':'width:300px',
                                             'autofocus':True,
                                            }
                                         ))
    
    weight = forms.DecimalField(label='',
                                required = True,
                                widget = forms.NumberInput(
                                    attrs={
                                        'min':'0',
                                        'max':'1',
                                        'step':'0.05',
                                        'type':'number',
                                        'placeholder':'Weight',
                                        'style': 'width:300px',
                                        }
                                    ))
    dueDate = forms.DateTimeField(input_formats=['%Y-%m-%dT%H:%M',],
                                  label='',
                                  required = True,
                                  widget = forms.DateTimeInput(
                                      attrs={
                                          'style':'width:300px',
                                          'placeholder':'Due Date',
                                          'onfocus':"(this.type='datetime-local')",
                                          'onblur':"(this.type='text')",
                                          },
                                      format='%Y-%m-%dT%H:%M'))

    totalMarks = forms.IntegerField(label='',
                                    required = True,
                                    widget =  forms.NumberInput(
                                        attrs={
                                            'min':'0',
                                            'type':'number',
                                            'placeholder':'Total Marks',
                                            'style': 'width:300px',
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
                               required = True,
                               widget = forms.NumberInput(
                                   attrs={
                                        'min':'0',
                                        'type':'number',
                                        'placeholder':'Marks',
                                        'style': 'width:300px',
                                        }
                                    ))
    description = forms.CharField(label='',
                                  required = True,
                                  widget = forms.TextInput(
                                      attrs={
                                          'maxlength':'100',
                                          'type':'text',
                                          'placeholder':'Description',
                                          'style':'width:300px',
                                          'autofocus':True,
                                          }
                                      ))
    
    field_order = ['required', 'description', 'marks']

    class Meta:
        model = AssessmentComponent
        fields = {'required','marks','description'}
                            
class StudentForm(forms.ModelForm):
    studentID = forms.IntegerField(label='',
                                   required = True,
                                   widget = forms.NumberInput(
                                   attrs={
                                       'min':'0',
                                       'max':'9999999',
                                       'type':'number',
                                       'placeholder':'Student ID',
                                       'style': 'width:300px',
                                       'autofocus':True,
                                       }
                                   ))
    
    firstName = forms.CharField(label='',
                                required = True,
                                widget = forms.TextInput(
                                    attrs={
                                        'maxlength':'128',
                                        'type':'text',
                                        'placeholder':'First Name',
                                        'style':'width:300px',
                                        }
                                    ))
    
    lastName = forms.CharField(label='',
                               required = True,
                               widget = forms.TextInput(
                                   attrs={
                                       'maxlength':'128',
                                       'type':'text',
                                       'placeholder':'Last Name',
                                       'style':'width:300px',
                                       }
                                   ))

    academicPlan = forms.ModelChoiceField(label='',
                                          required = True,
                                          empty_label="Academic Plan/Degree",
                                          queryset=Degree.objects.all(),
                                          widget=forms.Select(
                                              attrs={
                                                  'style':'width:300px',
                                                  }
                                              ))

    level = forms.ChoiceField(label='',
                              required = True,
                              choices=LEVEL_CHOICES,
                              widget=forms.Select(
                                  attrs={
                                      'style':'width:300px',
                                      }
                                  ))

    graduationDate = forms.DateField(input_formats=['%Y-%m-%d'],
                                     label='',
                                     required = True,
                                     widget = forms.DateInput(
                                         attrs={
                                             'placeholder':'Graduation Date',
                                             'onfocus':"(this.type='date')",
                                             'onblur':"(this.type='text')",
                                             'style':'width:300px',
                                             },
                                         format='%Y-%m-%d'))

    comments = forms.CharField(label='',
                               required = False,
                               widget = forms.TextInput(
                                   attrs={
                                       'maxlength':'2000',
                                       'type':'text',
                                       'placeholder':'Comments',
                                       'style':'width:400px;height:50px',
                                       }
                                   ))

    field_order = ['studentID', 'firstName', 'lastName','academicPlan','level','graduationDate','comments']
    
    class Meta:
        model = Student
        fields = ('studentID','firstName','lastName','academicPlan','level','graduationDate','comments')
		
