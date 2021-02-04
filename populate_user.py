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





if __name__ == "__main__":

    print_bar()
    #temparary admin account
    create_user("admin","admin","superuser")

    #temporary staff acounts no permissions
    create_user("staff1","staff1","")
    create_user("staff2","staff2","")
