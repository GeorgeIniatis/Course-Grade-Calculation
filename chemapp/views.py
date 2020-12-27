from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from chemapp.models import *
from chemapp.forms import *

def home(request):
    context_dict = {'boldmessage':'This is the home page'}
    return render(request,'chemapp/home.html', context=context_dict)

def about(request):
    return HttpResponse("This is the about page")

def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)
        if user:
            if user.is_active:
                login(request, user)
                return redirect(reverse('chemapp:home'))
            else:
                messages.error(request, 'Your account is disabled')
                return redirect(reverse('chemapp:login'))
        else:
            messages.error(request, 'Incorrect username or password')
            return redirect(reverse('chemapp:login'))
    else:
        return render(request, 'chemapp/login.html')

@login_required
def user_logout(request):
    logout(request)
    return redirect(reverse('chemapp:home'))
