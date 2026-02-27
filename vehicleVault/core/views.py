from django.shortcuts import render,redirect
from .forms import UserSignupForm, UserLoginForm
from django.contrib.auth import authenticate, login, logout
from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
# Create your views here.
def userSignupView(request):
    if request.method == 'POST':
        form = UserSignupForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            subject = "Welcome to VehicleVault"
            from_email = settings.EMAIL_HOST_USER
            to = [email]

            html_content = render_to_string(
                'emails/welcome_email.html', {'user_email': email}

            )

            text_content = strip_tags(html_content)
            email_message = EmailMultiAlternatives(
                subject, text_content, from_email, to
            )

            email_message.attach_alternative(html_content, "text/html")
            email_message.attach_file('static/images/red-car.jpg')
            email_message.send()

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

def homeView(request):
    return render(request, 'core/home.html')