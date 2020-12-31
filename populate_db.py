import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE','cs35_site_project.settings')

import django
django.setup()

from chemapp.models import *

import random

def print_bar():
    print("-------------------")



def create_user(username,password,permission):
    print("creating User: ")
    print("username: " + username)
    print("password: "+password)

    user_object = User.objects.create_user(username, password=password)

    if (permission == "superuser"):
        user_object.is_superuser = True
        user_object.is_staff = True
        print("permission: " + permission)
    else:
        print("permission: " + permission)

    user_object.save()
    print_bar()



def create_course(code, credits, name, shorthand, year, year_taught, semester,description, min_pass_grade, min_req_credit):
    print("Creating Course")
    print("code :"+ code)
    print("credits :" , credits)
    print("name :"+ name)
    print("shorthand :" + shorthand)
    print("year :" , year)
    print("year_taught :" + year_taught)
    print("semester :" , semester)
    print("description :" + description)
    print("min_pass_grade :" + min_pass_grade)
    print("min_req_credit :" + min_req_credit)

    Course.objects.create(
        code = code,
        creditsWorth = credits,
        name = name,
        shortHand = shorthand,
        year = year,
        academicYearTaught = year_taught,
        semester = semester,
        description = description,
        minimumPassGrade = min_pass_grade,
        minimumRequirementsForCredit = min_req_credit,
    )

    print_bar()



if __name__ == "__main__":

    print_bar()
    #temparary admin account
    create_user("admin","admin","superuser")

    #temporary staff acounts no permissions
    create_user("staff1","staff1","")
    create_user("staff2","staff2","")

    for i in range(5):
        create_course(f'CHEM-{i+4000}',  random.randint(5,21), f'chemistry-{i+1}', f'chem-{i+1}', random.randint(1,6), "2019-2020", random.randint(1,3), "temp desc", "B", "0.0")


    #create courses here
