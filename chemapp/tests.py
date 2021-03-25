from base64 import decode

import requests
from django.contrib.messages.storage.fallback import FallbackStorage
from django.contrib.sessions.backends import file
from django.contrib.sessions.middleware import SessionMiddleware
from django.test import RequestFactory, TestCase
from django.test.client import Client
from chemapp.views import *
import csv, io
from chemapp.models import *
import django
import os
from chemapp.forms import *
from populate_user import *
from django.contrib.auth.models import User
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "cs35-main.settings")# cs35-main_project
django.setup()
# Create your tests here.


#For runing the test, if show error like cant find path to somee.ico, may need change some setting outside.



class Test_For_project(TestCase):
   @classmethod
   def setUpClass(cls):
       create_user('admin', 'admin', 'superuser')
       # Degree.objects.create(degreeCode='F555-2222', name='basic-degree')


       # test_staff_0 = {'staffID': 111111, 'title': 'Prof', 'firstName': 'test', 'lastName': 'staff'}
       # request = RequestFactory.post('/chemapp/staff/add_staff/', data=test_staff_0)
       # middleware = SessionMiddleware()
       # middleware.process_request(request)
       # request.session.save()
       # request.user = self.tester
       # messages = FallbackStorage(request)
       # setattr(request, '_messages', messages)
       # add_staff(request)


   @classmethod
   def tearDownClass(cls):
       print('_______')


   def setUp(self):
       self.login_data = {'username': 'admin', 'password': 'admin'}
       self.headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.62 Safari/537.36'}
       self.test_degree = {'form-TOTAL_FORMS': 1, 'form-INITIAL_FORMS': 0, 'form-MIN_NUM_FORMS': 0,
                      'form-MAX_NUM_FORMS': 1000, 'form-0-name': 'Degree Name 1', 'form-0-degreeCode': 'F100-2208'}

       self.test_course = {'code': 'CHEM_1006',
                          'degree': 1,
                          'name':'Biological Chemistry 66',
                          'shortHand':'BIOCHEM1',
                          'creditsWorth':120,
                          'level':1,
                          'academicYearTaught':'19-20',
                          'semester':1,
                          'minimumPassGrade':'B3',
                          'minimumRequirementsForCredit':0.75,
                          'description':'abc',
                          'comments':'abc',
                          'courseColor':'#563d7c'}
       self.test_staff = {'staffID': 523375, 'title': 'Prof', 'firstName': 'Test', 'lastName': 'Subject'}
       self.test_student={
           'studentID':2234567,
           'firstName':'boy',
           'lastName':'girl',
           'academicPlan':1,
           'level':1,
           'graduationDate':'2021-03-01',
           'comments':'abc'
       }
       self.test_ass={
           'form-TOTAL_FORMS':1,
           'form-INITIAL_FORMS':0,
           'form-MIN_NUM_FORMS':0,
           'form-MAX_NUM_FORMS':1000,
           'form-0-assessmentName':'exam666',
           'form-0-weight':0.00,
           'form-0-totalMarks':120,
           'form-0-componentNumberNeeded':5,
           'form-0-dueDate':'12/12/2021/10:00'

       }


       self.test_ass_comp={
           'form-TOTAL_FORMS':1,
           'form-INITIAL_FORMS':'0',
           'form-MIN_NUM_FORMS': '0',
           'form-MAX_NUM_FORMS':'0',
           'form-0-required': '0',
           'form-0-lecturer':'0',
           'form-0-description': 'question 8',
           'form-0-marks':'20',

       }
       self.client.post('http://127.0.0.1:8000/chemapp/', data=self.login_data, headers=self.headers)
       self.tester=User.objects.get(username='admin')
       self.client.force_login(user=self.tester)
       self.factory = RequestFactory()

       add_staff(self.add_on_something('/chemapp/staff/add_staff/', self.test_staff))

       self.blankset = set([])

       #self.request = self.factory.post('/chemapp/', data=self.login_data)
       #self.middleware = SessionMiddleware()
       #self.middleware.process_request(self.request)
       #self.request.session.save()
       #self.messages = FallbackStorage(self.request)
       #setattr(self.request, '_messages', self.messages)

       #self.user_login(self.request)

       #print(requests.get('http://127.0.0.1:8000/chemapp/about').text)

   def test_user_login(self):
       request = self.factory.post('/chemapp/', data=self.login_data)
       middleware = SessionMiddleware()
       middleware.process_request(request)
       request.session.save()
       messages = FallbackStorage(request)
       setattr(request, '_messages', messages)
       user_login(request)
       assert user_login(request).status_code==302,'login test failed'

   #def test_about(self):
       #assert requests.get('http://127.0.0.1:8000/chemapp/home/').status_code == 200, 'home page failed'

   #def test_home(self):
       # assert requests.get('http://127.0.0.1:8000/chemapp/home').status_code == 200, 'move to degree failed'

   #def test_move_to_degrees(self):
       # assert requests.get('http://127.0.0.1:8000/chemapp/degrees').status_code == 200, 'move to degree failed'












   def add_on_something(self,htmlpath,data_add):
       request = self.factory.post(htmlpath, data=data_add)
       middleware = SessionMiddleware()
       middleware.process_request(request)
       request.session.save()
       request.user=self.tester
       messages = FallbackStorage(request)
       setattr(request, '_messages', messages)
       return request

   def test_on_add_degree(self):
         add_degree(self.add_on_something('/chemapp/degrees/add_degree/',self.test_degree))
         assert (Degree.objects.filter(degreeCode='F100-2208')) != [], 'add degree failed'


   def test_on_add_staff(self):
         assert (Staff.objects.filter(staffID=523375)) != [], 'staff_added failed'


   def test_on_add_course(self):
        add_degree(self.add_on_something('/chemapp/degrees/add_degree/', self.test_degree))
        add_staff(self.add_on_something('/chemapp/staff/add_staff/', self.test_staff))
        add_course(self.add_on_something('/chemapp/courses/add_course/',self.test_course))
        assert (Course.objects.filter(code='CHEM_1006')) != [],'course_added failed'

   def test_on_add_student(self):
        add_degree(self.add_on_something('/chemapp/degrees/add_degree/', self.test_degree))
        add_student(self.add_on_something('/chemapp/students/add_student/',self.test_student))
        assert (Student.objects.filter(studentID='2234567')) != [], 'student_added failed'

   def test_on_add_assesment(self):
        add_degree(self.add_on_something('/chemapp/degrees/add_degree/', self.test_degree))
        add_course(self.add_on_something('/chemapp/courses/add_course/', self.test_course))
        coursename_slug='chem_1006'+'-'+'f100-2208'
        add_assessments(self.add_on_something('/chemapp/courses/chem_1002-f100-2208/add_assessments/',self.test_ass),coursename_slug)
        assert (Assessment.objects.filter(assessmentName='exam66')) != [], 'assesment_added failed'

   def test_on_add_addesment_comp(self):
       upload_degree_csv(self.upload_via_csvs('/chemapp/degrees/upload_degree_csv/', 'd:\\degrees.csv'))
       upload_course_csv(self.upload_via_csvs('/chemapp/courses/upload_course_csv/', 'd:\\Courses.csv'))
       upload_assessment_csv(self.upload_via_csvs('/chemapp/courses/chem_1002-f100-2208/exam/upload_assessment_csv/','d:\\Assessments.csv'), 'chem_1002-f100-2208')
       add_assessmentComponents(self.add_on_something('/chemapp/courses/chem_1002-f100-2208/exam/add_assessmentComponents/', self.test_ass_comp),'chem_1002-f100-2208','exam')
       assert AssessmentComponent.objects.filter(description='question 8')!=[],'upload ass_comp_failed'


   def test_on_Degree_csv_upload(self):
        upload_degree_csv(self.upload_via_csvs('/chemapp/degrees/upload_degree_csv/', 'd:\\degrees.csv'))
        assert (Degree.objects.filter(name='test_degree')) != [], 'degree_upload_via_csv failed'

   def test_on_Course_csv_upload(self):
        upload_course_csv(self.upload_via_csvs('/chemapp/courses/upload_course_csv/', 'd:\\Courses.csv'))
        assert (Course.objects.filter(code='CHEM_1002')) != [], 'course_upload_via_csv failed'

   def test_on_Assesment_csv_upload(self):
        upload_degree_csv(self.upload_via_csvs('/chemapp/degrees/upload_degree_csv/', 'd:\\degrees.csv'))
        upload_course_csv(self.upload_via_csvs('/chemapp/courses/upload_course_csv/', 'd:\\Courses.csv'))
        upload_assessment_csv(self.upload_via_csvs('/chemapp/courses/chem_1002-f100-2208/exam/upload_assessment_csv/','d:\\Assessments.csv'),'chem_1002-f100-2208')
        assert (Assessment.objects.filter(assessmentName='exam')) != [], 'ASSESMENT_upload_via_csv failed'

   def test_on_Map_csv_upload(self):
       upload_degree_csv(self.upload_via_csvs('/chemapp/degrees/upload_degree_csv/', 'd:\\degrees.csv'))
       upload_course_csv(self.upload_via_csvs('/chemapp/courses/upload_course_csv/', 'd:\\Courses.csv'))
       upload_assessment_csv(self.upload_via_csvs('/chemapp/courses/chem_1002-f100-2208/exam/upload_assessment_csv/','d:\\Assessments.csv'), 'chem_1002-f100-2208')
       upload_map_csv(self.upload_via_csvs('/chemapp/courses/chem_1002-f100-2208/exam/map/','d:\\Map.csv'),'chem_1002-f100-2208','exam')
       assert Assessment.objects.get(slug='exam').map!=models.TextField(verbose_name="22 Scale Map",null=True,blank=True),'map upload failed'

   def test_on_student_csv_upload(self):
       upload_degree_csv(self.upload_via_csvs('/chemapp/degrees/upload_degree_csv/', 'd:\\degrees.csv'))
       upload_course_csv(self.upload_via_csvs('/chemapp/courses/upload_course_csv/', 'd:\\Courses.csv'))
       upload_student_csv(self.upload_via_csvs('/chemapp/courses/chem_1002-f100-2208/upload_student_csv/', 'd:\\Students.csv'),'chem_1002-f100-2208')
       assert (Student.objects.filter(studentID=2016655)!=[]),'student upload via csv faild'

   def test_on_student_assesment_info_csv_upload(self):
       upload_degree_csv(self.upload_via_csvs('/chemapp/degrees/upload_degree_csv/', 'd:\\degrees.csv'))
       upload_course_csv(self.upload_via_csvs('/chemapp/courses/upload_course_csv/', 'd:\\Courses.csv'))
       upload_assessment_csv(self.upload_via_csvs('/chemapp/courses/chem_1002-f100-2208/exam/upload_assessment_csv/','d:\\Assessments.csv'), 'chem_1002-f100-2208')
       upload_student_csv(self.upload_via_csvs('/chemapp/courses/chem_1002-f100-2208/upload_student_csv/', 'd:\\Students.csv'),'chem_1002-f100-2208')
       upload_student_assessment_info_csv(self.upload_via_csvs('/chemapp/courses/chem_1002-f100-2208/exam/upload_student_assessment_info_csv/','d:\\Student-Assessment-Info.csv'),'chem_1002-f100-2208','exam')


   def test_on_ass_comp_csv_upload(self):
       upload_degree_csv(self.upload_via_csvs('/chemapp/degrees/upload_degree_csv/', 'd:\\degrees.csv'))
       upload_course_csv(self.upload_via_csvs('/chemapp/courses/upload_course_csv/', 'd:\\Courses.csv'))
       upload_assessment_csv(self.upload_via_csvs('/chemapp/courses/chem_1002-f100-2208/exam/upload_assessment_csv/','d:\\Assessments.csv'), 'chem_1002-f100-2208')
       upload_assessment_comp_csv(self.upload_via_csvs('/chemapp/courses/chem_1002-f100-2208/exam/upload_assessment_comp_csv/','d:\\Assessment-Components.csv'),'chem_1002-f100-2208','exam')
       assert AssessmentComponent.objects.filter(description='Q1')!=[],'upload failed'

   def test_on_grade_via_csv(self):
       upload_degree_csv(self.upload_via_csvs('/chemapp/degrees/upload_degree_csv/', 'd:\\degrees.csv'))
       upload_course_csv(self.upload_via_csvs('/chemapp/courses/upload_course_csv/', 'd:\\Courses.csv'))
       upload_student_csv(self.upload_via_csvs('/chemapp/courses/chem_1002-f100-2208/upload_student_csv/', 'd:\\Students.csv'),'chem_1002-f100-2208')
       upload_assessment_csv(self.upload_via_csvs('/chemapp/courses/chem_1002-f100-2208/exam/upload_assessment_comp_csv/','d:\\Assessments.csv'), 'chem_1002-f100-2208')
       upload_assessment_comp_csv(self.upload_via_csvs('/chemapp/courses/chem_1002-f100-2208/exam/upload_assessment_comp_csv/','d:\\Assessment-Components.csv'), 'chem_1002-f100-2208', 'exam')
       upload_grades_csv(self.upload_via_csvs('/chemapp/courses/chem_1002-f100-2208/exam/q1/upload_grades_csv/', 'd:\\grades.csv',),'chem_1002-f100-2208','exam','q1')



   def upload_via_csvs(self,htmlpath,filepath):
         with open(filepath, 'r') as f:
           csv_add = {'file': f}
           request = self.factory.post(htmlpath, data=csv_add)
           middleware = SessionMiddleware()
           middleware.process_request(request)
           request.session.save()
           request.user = self.tester
           messages = FallbackStorage(request)
           setattr(request, '_messages', messages)
           return request


   def delete_something(self,htmlpath):
       request = self.factory.post(htmlpath)
       middleware = SessionMiddleware()
       middleware.process_request(request)
       request.session.save()
       request.user = self.tester
       messages = FallbackStorage(request)
       setattr(request, '_messages', messages)
       return request


   def test_on_delete_degree(self):
       upload_degree_csv(self.upload_via_csvs('/chemapp/degrees/upload_degree_csv/', 'd:\\degrees.csv'))
       delete_degree(self.delete_something('chemapp/degrees/f100-2208/delete_degree'),'f100-2208')
       assert Degree.objects.filter(name='Degree Name 1').count()==0 ,'delete degree failed'



   def test_on_delete_course(self):
       upload_degree_csv(self.upload_via_csvs('/chemapp/degrees/upload_degree_csv/', 'd:\\degrees.csv'))
       upload_course_csv(self.upload_via_csvs('/chemapp/courses/upload_course_csv/', 'd:\\Courses.csv'))
       delete_course(self.delete_something('/chemapp/courses/chem_1002-f100-2208/delete_course/'),'chem_1002-f100-2208')
       assert Course.objects.filter(code='CHEM_1002 ').count()==0 ,'delete degree failed'

   def test_on_delete_Ass(self):
       upload_degree_csv(self.upload_via_csvs('/chemapp/degrees/upload_degree_csv/', 'd:\\degrees.csv'))
       upload_course_csv(self.upload_via_csvs('/chemapp/courses/upload_course_csv/', 'd:\\Courses.csv'))
       upload_assessment_csv(self.upload_via_csvs('/chemapp/courses/chem_1002-f100-2208/exam/upload_assessment_csv/','d:\\Assessments.csv'), 'chem_1002-f100-2208')
       delete_assessment(self.delete_something('/chemapp/courses/chem_1002-f100-2208/exam/delete_assessment/'),'chem_1002-f100-2208','exam')
       assert Assessment.objects.filter(assessmentName='exam').count() == 0, 'delete assesment failed'

   def test_on_delete_Ass_comp(self):
       upload_degree_csv(self.upload_via_csvs('/chemapp/degrees/upload_degree_csv/', 'd:\\degrees.csv'))
       upload_course_csv(self.upload_via_csvs('/chemapp/courses/upload_course_csv/', 'd:\\Courses.csv'))
       upload_assessment_csv(self.upload_via_csvs('/chemapp/courses/chem_1002-f100-2208/exam/upload_assessment_csv/','d:\\Assessments.csv'), 'chem_1002-f100-2208')
       upload_assessment_comp_csv(self.upload_via_csvs('/chemapp/courses/chem_1002-f100-2208/exam/upload_assessment_comp_csv/', 'd:\\Assessment-Components.csv'), 'chem_1002-f100-2208', 'exam')
       delete_assessmentComponent(self.delete_something('/chemapp/courses/chem_1002-f100-2208/exam/q1/delete_component/'),
                         'chem_1002-f100-2208', 'exam','q1')
       assert AssessmentComponent.objects.filter(description='Q1').count() == 0, 'assesment comp delete failed'


   def test_on_staff_delete(self):
       delete_staff(self.delete_something('chemapp/staff/523375/delete_staff/'),523375)
       assert (Staff.objects.filter(staffID=523375)).count() == 0, 'staff_delete failed'


   # def test_on_edit_degree(self):
   #    upload_degree_csv(self.upload_via_csvs('/chemapp/degrees/upload_degree_csv/', 'd:\\degrees.csv'))
   #    edit_degree_data={'name':'gogo'}
   #    edit_degree(self.test_on_edit_something(htmlpath='/chemapp/degrees/f100-2208/edit_degree/',edit_data=edit_degree_data),'f100-2208')
   #    assert (Degree.objects.filter(name='f100-2208')).count()==0, 'degree_edit failed'
   #
   #
   # def test_on_edit_something(self,htmlpath,edit_data):
   #     request = self.factory.post(htmlpath, data=edit_data)
   #     middleware = SessionMiddleware()
   #     middleware.process_request(request)
   #     request.session.save()
   #     request.user = self.tester
   #     messages = FallbackStorage(request)
   #     setattr(request, '_messages', messages)
   #     return request




