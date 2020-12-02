from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

from chemapp.models import Category, Page
from chemapp.forms import UserForm, UserProfileForm, CategoryForm

def index(request):
    context_dict={'boldmessage':'Crunchy, creamy, cookie, candy, cupcake!'}
    return render(request,'chemapp/home.html', context=context_dict)

def about(request):
    return HttpResponse("This is the about page")

def show_category(request, category_name_slug):
    context_dict={}
    try:
        category = Category.objects.get(slug=category_name_slug)
        pages = Page.objects.filter(category=category)
        context_dict['pages'] = pages
        context_dict['category'] = category
    except Category.DoesNotExist:
        context_dict['category'] = None
        context_dict['pages'] = None
        return render(request,'rango/category.html', context=context_dict)

def user_registration(request):
    registered = False
    if request.method == 'POST':
        user_form = UserForm(request.POST)
        profile_form = UserProfileForm(request.POST)
        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save()
            user.set_password(user.password)
            user.save()
            profile = profile_form.save(commit=False)
            profile.user = user
            if 'profile_image' in request.FILES:
                profile.profile_image = request.FILES['profile_image']
            profile.save()
            registered = True
        else:
            print(user_form.errors, profile_form.errors)  #
    else:
        user_form = UserForm()
        profile_form = UserProfileForm()
    return render(request,
                  'chemapp/register.html',
                  context={'user_form': user_form,
                           'profile_form': profile_form,
                           'registered': registered})


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
                return HttpResponse("Your account is disabled.")
        else:
            print(f"Invalid login details: {username}, {password}")
            return HttpResponse("invalid login details supplied.")
    else:
        return render(request, 'chemapp/login.html')


@login_required
def user_logout(request):
    logout(request)
    return redirect(reverse('chemapp:home'))
