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

class DegreeForm(forms.ModelForm):
    degreeCode = forms.CharField(label='',
                                 widget = forms.TextInput(
                                     attrs={
                                         'maxlength':'30',
                                         'type':'text',
                                         'placeholder':'Degree Code',
                                         'style':'width:300px',
                                         'autofocus':True,
                                         'required':True,
                                         }
                                     ))

    class Meta:
        model = Degree
        fields = {'degreeCode'}

class CourseForm(forms.ModelForm):
    degree = forms.ModelChoiceField(label='',
                                    empty_label="Degree",
                                    queryset=Degree.objects.all(),
                                    widget=forms.Select(
                                        attrs={
                                            'style':'width:300px',
                                            'required':True,
                                            }
                                        ))

    level = forms.ChoiceField(label='',
                              choices=LEVEL_CHOICES,
                              widget=forms.Select(
                                  attrs={
                                      'style':'width:300px',
                                      'required':True,
                                      }
                                  ))
    
    class Meta:
        model = Course
        fields = {'code','degree','creditsWorth','name','shortHand','level','academicYearTaught',
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
                                             'autofocus':True,
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
                                          'style':'width:300px',
                                          'placeholder':'Due Date',
                                          'onfocus':"(this.type='datetime-local')",
                                          'onblur':"(this.type='text')",
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

    componentNumberNeeded = forms.IntegerField(label='',
                                               widget =  forms.NumberInput(
                                                   attrs={
                                                       'min':'0',
                                                       'type':'number',
                                                       'placeholder':'Number of Components Needed',
                                                       'style': 'width:300px',
                                                       'required':True,
                                                       }
                                                   ))
                                    
    field_order = ['assessmentName', 'weight', 'totalMarks', 'componentNumberNeeded', 'dueDate']

    class Meta:
        model = Assessment
        fields = {'assessmentName','weight','totalMarks','componentNumberNeeded','dueDate'}

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
                                          'autofocus':True,
                                          'required':True,
                                          }
                                      ))
    
    field_order = ['required', 'description', 'marks']

    class Meta:
        model = AssessmentComponent
        fields = {'required','marks','description'}
                            
class StudentForm(forms.ModelForm):
    studentID = forms.IntegerField(label='',
                                   widget = forms.NumberInput(
                                   attrs={
                                       'min':'0',
                                       'max':'9999999',
                                       'type':'number',
                                       'placeholder':'Student ID',
                                       'style': 'width:300px',
                                       'autofocus':True,
                                       'required':True,
                                       }
                                   ))
    
    firstName = forms.CharField(label='',
                                widget = forms.TextInput(
                                    attrs={
                                        'maxlength':'128',
                                        'type':'text',
                                        'placeholder':'First Name',
                                        'style':'width:300px',
                                        'required':True,
                                        }
                                    ))
    
    lastName = forms.CharField(label='',
                               widget = forms.TextInput(
                                   attrs={
                                       'maxlength':'128',
                                       'type':'text',
                                       'placeholder':'Last Name',
                                       'style':'width:300px',
                                       'required':True,
                                       }
                                   ))

    academicPlan = forms.ModelChoiceField(label='',
                                          empty_label="Academic Plan/Degree",
                                          queryset=Degree.objects.all(),
                                          widget=forms.Select(
                                              attrs={
                                                  'style':'width:300px',
                                                  'required':True,
                                                  }
                                              ))

    level = forms.ChoiceField(label='',
                              choices=LEVEL_CHOICES,
                              widget=forms.Select(
                                  attrs={
                                      'style':'width:300px',
                                      'required':True,
                                      }
                                  ))

    graduationDate = forms.DateField(input_formats=['%Y-%m-%d'],
                                     label='',
                                     widget = forms.DateInput(
                                         attrs={
                                             'placeholder':'Graduation Date',
                                             'onfocus':"(this.type='date')",
                                             'onblur':"(this.type='text')",
                                             'style':'width:300px',
                                             'required':True,
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
        fields = {'studentID','firstName','lastName','academicPlan','level','graduationDate','comments'}

class AssessmentGradeForm(forms.ModelForm):
    submissionDate = forms.DateTimeField(input_formats=['%Y-%m-%dT%H:%M',],
                                         label='',
                                         widget = forms.DateTimeInput(
                                             attrs={
                                                 'style':'width:300px',
                                                 'placeholder':'Date and Time submitted',
                                                 'onfocus':"(this.type='datetime-local')",
                                                 'onblur':"(this.type='text')",
                                                 'required':True,
                                                 },
                                             format='%Y-%m-%dT%H:%M'))

    noDetriment = forms.BooleanField(label='NDP',
                                     required = False,
                                     widget = forms.CheckboxInput(
                                         attrs={
                                             'placeholder':'NDP',
                                             }
                                         ))

    goodCause = forms.BooleanField(label='Good Cause',
                                   required = False,
                                   widget = forms.CheckboxInput(
                                       attrs={
                                           'placeholder':'Goo Cause',
                                           }
                                       ))

    field_order = ['noDetriment', 'goodCause', 'submissionDate']
    
    class Meta:
        model = AssessmentGrade
        fields = {'submissionDate','noDetriment','goodCause'}

class AssessmentComponentGradeForm(forms.ModelForm):
    description =  forms.CharField(label='',
                                   widget = forms.TextInput(
                                       attrs={
                                           'type':'text',
                                           'style':'width:300px',
                                           }
                                       ))

    assessmentComponent = forms.ModelChoiceField(label='',
                                                 queryset=AssessmentComponent.objects.all(),
                                                 widget=forms.TextInput(
                                                     attrs={
                                                         'type':'hidden',
                                                         'style':'width:300px',
                                                         }
                                                     ))

    grade = forms.DecimalField(label='',
                               required=False,
                               widget = forms.NumberInput(
                                   attrs={
                                        'min':'0',
                                        'step':'0.01',
                                        'type':'number',
                                        'placeholder':'Grade',
                                        'style': 'width:300px',
                                        }
                                   ))

    field_order = ['description','assessmentComponent', 'grade']
    
    class Meta:
        model = AssessmentComponentGrade
        fields= {'description','assessmentComponent','grade'}
		
