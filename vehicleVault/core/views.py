from django.shortcuts import render,redirect
from .forms import UserSignupForm, UserLoginForm
from django.contrib.auth import authenticate, login, logout

# Create your views here.
def userSignupView(request):
    if request.method == 'POST':
        form = UserSignupForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
        else:
            return render(request, 'core/signup.html', {'form': form})
    else:
        form = UserSignupForm()
    return render(request, 'core/signup.html', {'form': form})

def userLoginView(request):
    if request.method == 'POST':
        form = UserLoginForm(request.POST or None)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password')
           
            user = authenticate(request, email=email, password=password)
            if user:
                login(request, user)
                if user.role == 'admin':
                    return redirect('admin-dashboard')
                elif user.role == 'user':
                    return redirect('user-dashboard')
                    
            else:
                return render(request, 'core/login.html', {'form': form, 'error': 'Invalid email or password'})
    else:
        form = UserLoginForm()
    return render(request, 'core/login.html', {'form': form})


def userLogoutView(request):
    logout(request)
    return redirect('login')