from django.shortcuts import render, redirect
from userauth.forms import UserRegisterForm
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.conf import settings
from userauth.models import User
from django.contrib.auth.decorators import login_required
# User = settings.AUTH_USER_MODEL

# Create your views here.

def register_view(request):
    if request.method == "POST":
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            new_user = form.save()
            username = form.cleaned_data.get("username")
            messages.success(request, f"Hey {username}, you successfully registered!")
            new_user = authenticate(username=form.cleaned_data['email'], password=form.cleaned_data['password1'])
            login(request, new_user)
            return redirect("core:index")
    else:
        form = UserRegisterForm()

    context = {
        'form': form,
    }
    return render(request, 'userauth/sign-up.html', context)


def login_view(request):
    if request.user.is_authenticated:
        messages.warning(request, f"You are already logged in!")
        return redirect("core:index")

    if request.method == "POST":
        email = request.POST.get('email').lower()
        password = request.POST.get('password')

        try:
            user = User.objects.get(email=email)
            user = authenticate(request, email=email, password=password)

            if user is not None:
                login(request, user)
                messages.success(request, f"You are logged in!")
                return redirect('core:index')
            else:
                messages.warning(request, "Username or password is incorrect!")
        except:
            messages.warning(request, "User does not exist!")

    context = {

    }
    return render(request, "userauth/sign-in.html", context)


def logout_view(request):
    logout(request)
    messages.success(request, "You are logged out!")
    return redirect("userauth:sign-in")