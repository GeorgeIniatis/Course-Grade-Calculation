# Team Project H 2020 Group CS35
 Welcome to our Team Project. This project aims to develop a system for the School of Chemistry at the University of Glasgow that aids with the calculation of assessment and course grades.
Currently, the school uses huge excel files, with each lecturer having a different one, to accomplish these calculations. These files are very complicated, time-consuming, and cause unnecessary stress to the staff. 
The system will try to centralize and automate the process, where possible, requiring very little input from the system users.

 Data Entry Flow:


1. Add Staff Members. This also creates accounts that enable access to the site.
2. Add Degrees.
3. Add Courses.
4. Add Assessments (Exam/Labs) for those courses.
5. Add Assessment Components (Questions) for those Assessments.
6. Upload a Grade Map for that Assessment.
7. Add Students to the course.
8. Either Upload Student NDP/GC/Submission Date and then Upload the Grades for each Assessment Component or add Grades Manually for each Student.
9. Export the Course Grades when available

*Most of these tasks can be done manually or via CSV upload. There is a template for you to copy paste on the upload page.

*All tasks can be Edited and Deleted if required by the user at any point.

*Staff can access their accounts by using their first and last name, without any spaces, as their username and their staff id as password. The passwords can be changed through the admin page

### Running project locally

First clone the repository

 `$ git clone https://github.com/GeorgeIniatis/Course-Grade-Calculation.git`

Install Dependencies e.g. on Virtual Machine/server

 `$ pip install -r requirements.txt`

 When you have the required Depenencies for the enviroment we can run

 `$ python manage.py makemigrations chemapp`

 `$ python manage.py migrate`

The CMD below will generate some default admin and user accounts. NOT for production!
You will see a print out on the console of all the data used to populate the database, such as username and passwords for the temporary accounts.

  `$ python populate_user.py`

Run CMD below to start the WebApp.

 `$ python manage.py runserver`

 This will start our project. The site will be bare as this will be a fresh database file.



 ## License
[GNU v3.0](https://choosealicense.com/licenses/gpl-3.0/#)
