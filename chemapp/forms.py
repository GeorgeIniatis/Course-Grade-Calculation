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

SEMESTER_CHOICES = [
    ('', 'Semester'),
    ('1', 'Semester 1'),
    ('2', 'Semester 2'),
    ('Both', 'Both'),
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
    degreeCode = forms.CharField(label='Degree Code',
                                 help_text='4A-ABC',
                                 widget = forms.TextInput(
                                     attrs={
                                         'maxlength':'30',
                                         'type':'text',
                                         'style':'width:300px',
                                         'autofocus':True,
                                         'required':True,
                                         'class':'form-control'
                                         }
                                     ))

    name = forms.CharField(label='Name',
                           help_text='BSci Chemistry',
                           widget = forms.TextInput(
                               attrs={
                                   'maxlength':'200',
                                   'type':'text',
                                   'style':'width:300px',
                                   'required':True,
                                   'class':'form-control'
                                   }
                               ))

    class Meta:
        model = Degree
        fields = {'degreeCode','name'}

class CourseForm(forms.ModelForm):
    code = forms.CharField(label='Code',
                           help_text='CHEM1006',
                           widget = forms.TextInput(
                               attrs={
                                   'maxlength':'30',
                                   'type':'text',
                                   'id':'floatingCode',
                                   'placeholder':'Code',
                                   'class':'form-control',
                                   'style':'width:100%;text-transform:uppercase',
                                   'autofocus':True,
                                   'required':True,
                                   }
                               ))

    degree = forms.ModelChoiceField(label='Degree',
                                    help_text='4A-ABC',
                                    empty_label="Select a choice",
                                    queryset=Degree.objects.all(),
                                    widget=forms.Select(
                                        attrs={
                                            'style':'width:100%',
                                            'required':True,
                                            'id':'floatingDegree',
                                            'class':'form-select',
                                            }
                                        ))

    name = forms.CharField(label='Name',
                           help_text='Biological Chemistry 1',
                           widget = forms.TextInput(
                               attrs={
                                   'maxlength':'200',
                                   'type':'text',
                                   'placeholder':'Name',
                                   'id':'floatingName',
                                   'class':'form-control ',
                                   'style':'width:300px',
                                   'required':True,
                                   }
                               ))

    shortHand = forms.CharField(label='Shorthand',
                                help_text='BIOCHEM1',
                                widget = forms.TextInput(
                                    attrs={
                                        'maxlength':'30',
                                        'type':'text',
                                        'placeholder':'Shorthand',
                                        'id':'floatingShorthand',
                                        'class':'form-control',
                                        'style':'width:300px;text-transform:uppercase',
                                        'required':True,
                                        }
                                    ))

    creditsWorth = forms.IntegerField(label='Credits Worth',
                                      help_text='20, Between 5-120 credits',
                                      widget =  forms.NumberInput(
                                          attrs={
                                              'min':'5',
                                              'max':'120',
                                              'type':'number',
                                              'placeholder':'Credits Worth',
                                              'class':'form-control',
                                              'style': 'width:300px',
                                              'required':True,
                                              }
                                          ))

    level = forms.ChoiceField(label='Level',
                              help_text='Level 1',
                              choices=LEVEL_CHOICES,
                              widget=forms.Select(
                                  attrs={
                                      'style':'width:300px',
                                      'required':True,
                                      'class':'form-select',
                                      }
                                  ))

    academicYearTaught = forms.CharField(label='Academic Year Taught',
                                         help_text='19-20',
                                         widget = forms.TextInput(
                                             attrs={
                                                 'maxlength':'5',
                                                 'type':'text',
                                                 'placeholder':'Academic Year Taught',
                                                 'style':'width:300px',
                                                 'required':True,
                                                 'class':'form-control',
                                                 }
                                             ))

    semester = forms.ChoiceField(label='Semester',
                                 help_text='Semester 1',
                                 choices=SEMESTER_CHOICES,
                                 widget=forms.Select(
                                     attrs={
                                         'style':'width:300px',
                                         'required':True,
                                         'class':'form-select',
                                         }
                                     ))

    minimumPassGrade = forms.CharField(label='Minimum Pass Grade',
                                       help_text='B3',
                                       widget = forms.TextInput(
                                           attrs={
                                               'maxlength':'2',
                                               'type':'text',
                                               'placeholder':'Minimum Pass Grade',
                                               'class':'form-control',
                                               'style':'width:300px;text-transform:uppercase',
                                               'required':True,
                                               }
                                           ))

    minimumRequirementsForCredit = forms.DecimalField(label='Minimum Requirements For Credit',
                                                      help_text='0.75',
                                                      widget = forms.NumberInput(
                                                          attrs={
                                                              'min':'0',
                                                              'max':'1',
                                                              'step':'0.05',
                                                              'type':'number',
                                                              'placeholder':'Minimum Requirements For Credit',
                                                              'class':'form-control',
                                                              'style': 'width:300px',
                                                              'required':True,
                                                              }
                                                          ))

    courseColor = forms.CharField(label='Color',
                                  widget=forms.TextInput(
                                      attrs={
                                          'type': 'color',
                                          'class':'form-control form-control-color',
                                          'title':'Choose course color',
                                          'style':'width:300px',
                                          }
                                      ))

    description = forms.CharField(label='Description',
                                  widget = forms.TextInput(
                                      attrs={
                                          'maxlength':'2000',
                                          'type':'text',
                                          'placeholder':'Description',
                                          'class':'form-control',
                                          'style':'width:400px;height:50px',
                                          'required':True,
                                          }
                                      ))

    comments = forms.CharField(label='Comments',
                               required = False,
                               widget = forms.TextInput(
                                   attrs={
                                       'maxlength':'2000',
                                       'type':'text',
                                       'placeholder':'Comments',
                                       'class':'form-control',
                                       'style':'width:400px;height:50px',
                                       }
                                   ))

    field_order = ['code', 'degree', 'name', 'shortHand', 'creditsWorth','level','academicYearTaught',
                   'semester','minimumPassGrade','minimumRequirementsForCredit','description','comments','courseColor']

    class Meta:
        model = Course
        fields = {'code','degree','creditsWorth','name','shortHand','level','academicYearTaught',
                  'semester','description','comments','minimumPassGrade',
                  'minimumRequirementsForCredit','courseColor'}

class AssessmentForm(forms.ModelForm):
    assessmentName = forms.CharField(label='',
                                     help_text='Exam',
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
                                help_text='0.80',
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
                                  help_text='12/01/2021 10:00',
                                  widget = forms.DateTimeInput(
                                      attrs={
                                          'placeholder':'Due Date and Time',
                                          'onfocus':"(this.type='datetime-local')",
                                          'onblur':"(this.type='text')",
                                          'style':'width:300px',
                                          'required':True,
                                          },
                                      format='%Y-%m-%dT%H:%M'))

    totalMarks = forms.IntegerField(label='',
                                    help_text='120',
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
                                               help_text='3,Includes required and optional components',
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
                               help_text='20',
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
                                  help_text='Question 1',
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

    gapYear = forms.BooleanField(label='Gap Year',
                                 required = False,
                                 widget = forms.CheckboxInput(
                                     attrs={
                                         'placeholder':'Required',
                                         }
                                     ))

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

    field_order = ['gapYear','studentID', 'firstName', 'lastName','academicPlan','level','graduationDate','comments']

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
                                           'placeholder':'Good Cause',
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

class FinalAssessmentGradeForm(forms.ModelForm):

    finalGrade = forms.DecimalField(label='',
                                    widget = forms.NumberInput(
                                        attrs={
                                            'min':'0',
                                            'step':'0.01',
                                            'type':'number',
                                            'placeholder':'Final Grade',
                                            'style': 'width:300px',
                                            'autofocus':True,
                                            'required':True,
                                            }
                                       ))

    class Meta:
        model = AssessmentGrade
        fields = {'finalGrade'}
