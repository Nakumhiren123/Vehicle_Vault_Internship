from django.shortcuts import render, redirect
from .forms import UserSignupForm, UserLoginForm, ForgotPasswordForm, ResetPasswordForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth import login as auth_login
from django.contrib.auth import update_session_auth_hash
from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.http import JsonResponse
from django.utils import timezone
from django.conf import settings
import random
import string


# ============================================================
#  SIGNUP VIEW — role always forced to 'user' (security fix)
# ============================================================
def userSignupView(request):
    if request.method == 'POST':
        form = UserSignupForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            raw_pw = form.cleaned_data.get('password1', '')
            user.set_password(raw_pw)
            user.role = 'user'          # SECURITY FIX: always 'user', never from form
            if hasattr(user, 'raw_password'):
                user.raw_password = raw_pw
            user.save()

            email      = form.cleaned_data['email']
            first_name = form.cleaned_data.get('first_name', '')
            last_name  = form.cleaned_data.get('last_name', '')

            subject    = "Welcome to VehicleVault 🚗"
            from_email = settings.EMAIL_HOST_USER
            to         = [email]

            html_content = render_to_string(
                'emails/welcome_email.html',
                {'first_name': first_name, 'last_name': last_name, 'user_email': email}
            )
            text_content = strip_tags(html_content)
            email_message = EmailMultiAlternatives(subject, text_content, from_email, to)
            email_message.attach_alternative(html_content, "text/html")

            import os
            pdf_path = os.path.join(settings.BASE_DIR, 'static', 'pdf', 'vehiclevault_welcome.pdf')
            if os.path.exists(pdf_path):
                email_message.attach_file(pdf_path)

            try:
                email_message.send()
            except Exception:
                pass  # don't break signup if email fails

            return redirect('login')
        else:
            return render(request, 'core/signup.html', {'form': form})
    else:
        form = UserSignupForm()
    return render(request, 'core/signup.html', {'form': form})


# ============================================================
#  LOGIN VIEW  — step 1: credentials → send OTP
# ============================================================
def userLoginView(request):
    form = UserLoginForm()

    if request.method == 'POST' and request.POST.get('step') == 'credentials':
        form = UserLoginForm(request.POST)
        if form.is_valid():
            email    = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user     = authenticate(request, email=email, password=password)

            if user is not None:
                otp = ''.join(random.choices(string.digits, k=6))
                user.otp            = otp
                user.otp_created_at = timezone.now()
                user.save(update_fields=['otp', 'otp_created_at'])

                send_mail(
                    subject='Your VehicleVault Login OTP',
                    message=f'Your one-time password is: {otp}\n\nThis code expires in 5 minutes.',
                    from_email=settings.EMAIL_HOST_USER,
                    recipient_list=[email],
                    fail_silently=False,
                )

                request.session['otp_email'] = email
                return render(request, 'core/login.html', {
                    'form': UserLoginForm(),
                    'show_otp_step': True,
                    'otp_email': email,
                })
            else:
                return render(request, 'core/login.html', {
                    'form': form,
                    'login_error': 'Invalid email or password.',
                })

    return render(request, 'core/login.html', {'form': form})


# ============================================================
#  VERIFY OTP VIEW
# ============================================================
def verify_otp(request):
    from .models import User

    if request.method == 'POST':
        email     = request.POST.get('email', '').strip()
        submitted = request.POST.get('otp',   '').strip()

        if request.session.get('otp_email') != email:
            return render(request, 'core/login.html', {
                'form': UserLoginForm(),
                'show_otp_step': True,
                'otp_email':     email,
                'otp_error':     'Session mismatch. Please log in again.',
            })

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return redirect('login')

        if user.otp_created_at:
            elapsed = (timezone.now() - user.otp_created_at).total_seconds()
            if elapsed > 300:
                return render(request, 'core/login.html', {
                    'form': UserLoginForm(),
                    'show_otp_step': True,
                    'otp_email':     email,
                    'otp_error':     'OTP has expired. Please log in again.',
                })

        if user.otp == submitted:
            user.otp            = None
            user.otp_created_at = None
            user.save(update_fields=['otp', 'otp_created_at'])
            del request.session['otp_email']

            user.backend = 'core.backends.EmailBackend'
            auth_login(request, user)

            if user.role == 'admin':
                return redirect('admin-dashboard')
            return redirect('user-dashboard')

        else:
            return render(request, 'core/login.html', {
                'form': UserLoginForm(),
                'show_otp_step': True,
                'otp_email':     email,
                'otp_error':     'Incorrect OTP. Please try again.',
            })

    return redirect('login')


# ============================================================
#  RESEND OTP VIEW  (AJAX POST)
# ============================================================
def resend_otp(request):
    from core.models import User

    if request.method == 'POST':
        email = request.POST.get('email', '').strip()

        if request.session.get('otp_email') != email:
            return JsonResponse({'success': False, 'error': 'Session mismatch.'})

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'User not found.'})

        otp = ''.join(random.choices(string.digits, k=6))
        user.otp            = otp
        user.otp_created_at = timezone.now()
        user.save(update_fields=['otp', 'otp_created_at'])

        send_mail(
            subject='Your VehicleVault Login OTP (Resent)',
            message=f'Your new one-time password is: {otp}\n\nThis code expires in 5 minutes.',
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[email],
            fail_silently=False,
        )

        return JsonResponse({'success': True})

    return JsonResponse({'success': False})


# ============================================================
#  FORGOT PASSWORD — Step 1: enter email → send OTP
# ============================================================
def forgot_password(request):
    form = ForgotPasswordForm()

    if request.method == 'POST':
        form = ForgotPasswordForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            from .models import User
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                # Don't reveal if email exists — show same success message
                return render(request, 'core/forgot_password.html', {
                    'form': ForgotPasswordForm(),
                    'sent': True,
                    'email': email,
                })

            # Generate OTP
            otp = ''.join(random.choices(string.digits, k=6))
            user.otp            = otp
            user.otp_created_at = timezone.now()
            user.save(update_fields=['otp', 'otp_created_at'])

            send_mail(
                subject='VehicleVault — Password Reset OTP',
                message=(
                    f'You requested a password reset for your VehicleVault account.\n\n'
                    f'Your OTP is: {otp}\n\n'
                    f'This code expires in 10 minutes.\n'
                    f'If you did not request this, ignore this email.'
                ),
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[email],
                fail_silently=False,
            )

            request.session['reset_email'] = email
            return render(request, 'core/forgot_password.html', {
                'form': ForgotPasswordForm(),
                'sent': True,
                'email': email,
            })

    return render(request, 'core/forgot_password.html', {'form': form})


# ============================================================
#  FORGOT PASSWORD — Step 2: verify OTP
# ============================================================
def forgot_verify_otp(request):
    if request.method == 'POST':
        email     = request.POST.get('email', '').strip()
        submitted = request.POST.get('otp',   '').strip()

        if request.session.get('reset_email') != email:
            return render(request, 'core/forgot_password.html', {
                'form': ForgotPasswordForm(),
                'sent':       True,
                'email':      email,
                'otp_error':  'Session mismatch. Please start again.',
            })

        from .models import User
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return redirect('forgot_password')

        # Check OTP expiry (10 minutes for password reset)
        if user.otp_created_at:
            elapsed = (timezone.now() - user.otp_created_at).total_seconds()
            if elapsed > 600:
                return render(request, 'core/forgot_password.html', {
                    'form': ForgotPasswordForm(),
                    'sent':      True,
                    'email':     email,
                    'otp_error': 'OTP expired. Please request a new one.',
                })

        if user.otp == submitted:
            # OTP correct — store verified flag in session, go to reset form
            request.session['reset_verified_email'] = email
            user.otp            = None
            user.otp_created_at = None
            user.save(update_fields=['otp', 'otp_created_at'])
            return redirect('reset_password_form')
        else:
            return render(request, 'core/forgot_password.html', {
                'form': ForgotPasswordForm(),
                'sent':      True,
                'email':     email,
                'otp_error': 'Incorrect OTP. Please try again.',
            })

    return redirect('forgot_password')


# ============================================================
#  FORGOT PASSWORD — Step 3: enter new password
# ============================================================
def reset_password_form(request):
    email = request.session.get('reset_verified_email')
    if not email:
        return redirect('forgot_password')

    form = ResetPasswordForm()

    if request.method == 'POST':
        form = ResetPasswordForm(request.POST)
        if form.is_valid():
            from .models import User
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                return redirect('forgot_password')

            new_pw = form.cleaned_data['new_password1']
            user.set_password(new_pw)
            if hasattr(user, 'raw_password'):
                user.raw_password = new_pw
            user.save()

            # Clear session
            del request.session['reset_verified_email']
            if 'reset_email' in request.session:
                del request.session['reset_email']

            return render(request, 'core/reset_password_form.html', {
                'form': form,
                'success': True,
            })

    return render(request, 'core/reset_password_form.html', {'form': form, 'email': email})


# ============================================================
#  RESET PASSWORD (from profile modal — logged in users)
# ============================================================
def reset_password(request):
    if not request.user.is_authenticated:
        return JsonResponse({'success': False, 'error': 'Not authenticated.'})

    if request.method == 'POST':
        current = request.POST.get('current_password', '')
        new_pw1 = request.POST.get('new_password1',    '')
        new_pw2 = request.POST.get('new_password2',    '')

        if not request.user.check_password(current):
            return JsonResponse({'success': False, 'error': 'Current password is incorrect.'})
        if new_pw1 != new_pw2:
            return JsonResponse({'success': False, 'error': 'New passwords do not match.'})
        if len(new_pw1) < 8:
            return JsonResponse({'success': False, 'error': 'Password must be at least 8 characters.'})

        request.user.set_password(new_pw1)
        if hasattr(request.user, 'raw_password'):
            request.user.raw_password = new_pw1
        request.user.save()
        update_session_auth_hash(request, request.user)
        return JsonResponse({'success': True})

    return JsonResponse({'success': False, 'error': 'Invalid request.'})


# ============================================================
#  CONTACT FORM
# ============================================================
def send_contact_email(request):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Invalid request method.'})

    fname   = request.POST.get('fname',   '').strip()
    lname   = request.POST.get('lname',   '').strip()
    email   = request.POST.get('email',   '').strip()
    subject = request.POST.get('subject', '').strip()
    message = request.POST.get('message', '').strip()

    if not all([fname, lname, email, subject, message]):
        return JsonResponse({'success': False, 'error': 'All fields are required.'})

    import re
    if not re.match(r'^[^\s@]+@[^\s@]+\.[^\s@]+$', email):
        return JsonResponse({'success': False, 'error': 'Please enter a valid email address.'})

    try:
        send_mail(
            subject=f'[VehicleVault Contact] {subject}',
            message=(
                f'New contact message from VehicleVault:\n\n'
                f'Name:    {fname} {lname}\n'
                f'Email:   {email}\n'
                f'Subject: {subject}\n\n'
                f'Message:\n{message}\n'
            ),
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[settings.EMAIL_HOST_USER],
            fail_silently=False,
        )
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': f'Email could not be sent: {str(e)}'})


# ============================================================
#  LOGOUT / HOME
# ============================================================
def userLogoutView(request):
    logout(request)
    return redirect('login')


def homeView(request):
    from compare.models import Car
    # Pick a featured car that has a 3D model, fall back to any active car
    featured_car = (
        Car.objects.filter(status=True, model_3d__isnull=False).exclude(model_3d='').first()
        or Car.objects.filter(status=True).first()
    )
    return render(request, 'core/home.html', {'featured_car': featured_car})



# from django.shortcuts import render,redirect
# from .forms import UserSignupForm, UserLoginForm
# from django.contrib.auth import authenticate, login, logout
# from django.contrib.auth import login as auth_login
# from django.contrib.auth import update_session_auth_hash
# from django.core.mail import send_mail, EmailMultiAlternatives
# from django.template.loader import render_to_string
# from django.utils.html import strip_tags
# from django.http import JsonResponse
# from django.utils import timezone
# from django.conf import settings
# import random
# import string
# # Create your views here.
# def userSignupView(request):
#     if request.method == 'POST':
#         form = UserSignupForm(request.POST)
#         if form.is_valid():

#             # Save user first
#             user = form.save(commit=False)
#             raw_pw = form.cleaned_data.get('password1', '')
#             user.set_password(raw_pw)
#             if hasattr(user, 'raw_password'):
#                 user.raw_password = raw_pw
#             user.save()

#             # Email details — TO = new user's email, FROM = EMAIL_HOST_USER
#             email      = form.cleaned_data['email']        # new user's email
#             first_name = form.cleaned_data.get('first_name', '')
#             last_name  = form.cleaned_data.get('last_name', '')

#             subject    = "Welcome to VehicleVault 🚗"
#             from_email = settings.EMAIL_HOST_USER          # your Gmail
#             to         = [email]                           # ← new user's inbox

#             html_content = render_to_string(
#                 'emails/welcome_email.html',
#                 {
#                     'first_name': first_name,
#                     'last_name':  last_name,
#                     'user_email': email,
#                 }
#             )
#             text_content = strip_tags(html_content)

#             email_message = EmailMultiAlternatives(subject, text_content, from_email, to)
#             email_message.attach_alternative(html_content, "text/html")

#             # Attach PDF brochure — absolute path via BASE_DIR (safe on all OSes)
#             import os
#             pdf_path = os.path.join(settings.BASE_DIR, 'static', 'pdf', 'vehiclevault_welcome.pdf')
#             if os.path.exists(pdf_path):
#                 email_message.attach_file(pdf_path)

#             email_message.send()

#             return redirect('login')
#         else:
#             return render(request, 'core/signup.html', {'form': form})
#     else:
#         form = UserSignupForm()
#     return render(request, 'core/signup.html', {'form': form})

# # def userLoginView(request):
# #     if request.method == 'POST':
# #         form = UserLoginForm(request.POST or None)
# #         if form.is_valid():
# #             email = form.cleaned_data.get('email')
# #             password = form.cleaned_data.get('password')
           
# #             user = authenticate(request, email=email, password=password)
# #             if user:
# #                 login(request, user)
# #                 if user.role == 'admin':
# #                     return redirect('admin-dashboard')
# #                 elif user.role == 'user':
# #                     return redirect('user-dashboard')
                    
# #             else:
# #                 return render(request, 'core/login.html', {'form': form, 'error': 'Invalid email or password'})
# #     else:
# #         form = UserLoginForm()
# #     return render(request, 'core/login.html', {'form': form})

# # ============================================================
# #  Add these imports at the top of your views.py
# # ============================================================
# # from django.core.mail import send_mail
# # from django.contrib.auth import login as auth_login, authenticate
# # from django.http import JsonResponse
# # import random, string

# # ============================================================
# #  Add these to core/models.py  (or wherever your User lives)
# #  so you can store raw_password and OTP on the user model.
# #
# #  Run:  python manage.py makemigrations && python manage.py migrate
# # ============================================================
# #
# # class User(AbstractBaseUser, ...):
# #     ...
# #     raw_password = models.CharField(max_length=255, blank=True, null=True)
# #     otp          = models.CharField(max_length=6,   blank=True, null=True)
# #     otp_created_at = models.DateTimeField(null=True, blank=True)


# # ============================================================
# #  LOGIN VIEW  (replaces your existing login view)
# # ============================================================

# def userLoginView(request):
   
#     form = UserLoginForm()

#     # ── Step 1: validate credentials, send OTP ──
#     if request.method == 'POST' and request.POST.get('step') == 'credentials':
#         form = UserLoginForm(request.POST)
#         if form.is_valid():
#             email    = form.cleaned_data['email']
#             password = form.cleaned_data['password']
#             user     = authenticate(request, email=email, password=password)

#             if user is not None:
#                 # Generate 6-digit OTP
#                 otp = ''.join(random.choices(string.digits, k=6))
#                 user.otp            = otp
#                 user.otp_created_at = timezone.now()
#                 user.save(update_fields=['otp', 'otp_created_at'])

#                 # Send OTP email
#                 send_mail(
#                     subject='Your VehicleVault Login OTP',
#                     message=f'Your one-time password is: {otp}\n\nThis code expires in 5 minutes.',
#                     from_email=settings.EMAIL_HOST_USER,
#                     recipient_list=[email],
#                     fail_silently=False,
#                 )

#                 # Store email in session for OTP step
#                 request.session['otp_email'] = email

#                 return render(request, 'core/login.html', {
#                     'form': UserLoginForm(),
#                     'show_otp_step': True,
#                     'otp_email': email,
#                 })
#             else:
#                  return render(request, 'core/login.html', {
#                     'form': form,
#                     'login_error': 'Invalid email or password.',
#                 })

#     return render(request, 'core/login.html', {'form': form})


# # ============================================================
# #  VERIFY OTP VIEW
# # ============================================================
# def verify_otp(request):
#     from .models import User

#     if request.method == 'POST':
#         email     = request.POST.get('email', '').strip()
#         submitted = request.POST.get('otp',   '').strip()

#         # Validate session matches
#         if request.session.get('otp_email') != email:
#             return render(request, 'core/login.html', {
#                 'form': UserLoginForm(),
#                 'show_otp_step': True,
#                 'otp_email':     email,
#                 'otp_error':     'Session mismatch. Please log in again.',
#             })

#         try:
#             user = User.objects.get(email=email)
#         except User.DoesNotExist:
#             return redirect('login')

#         # Check OTP expiry (5 minutes)
#         if user.otp_created_at:
#             elapsed = (timezone.now() - user.otp_created_at).total_seconds()
#             if elapsed > 300:
#                 return render(request, 'core/login.html', {
#                     'form': UserLoginForm(),
#                     'show_otp_step': True,
#                     'otp_email':     email,
#                     'otp_error':     'OTP has expired. Please log in again.',
#                 })

#         if user.otp == submitted:
#             # Clear OTP fields
#             user.otp            = None
#             user.otp_created_at = None
#             user.save(update_fields=['otp', 'otp_created_at'])
#             del request.session['otp_email']

#             # Log user in
#             user.backend = 'django.contrib.auth.backends.ModelBackend'
#             auth_login(request, user)

#             # Redirect based on role
#             if user.role == 'admin':
#                 return redirect('admin-dashboard')
#             return redirect('user-dashboard')

#         else:
#             return render(request, 'core/login.html', {
#                 'form': UserLoginForm(),
#                 'show_otp_step': True,
#                 'otp_email':     email,
#                 'otp_error':     'Incorrect OTP. Please try again.',
#             })

#     return redirect('login')


# # ============================================================
# #  RESEND OTP VIEW  (AJAX POST)
# # ============================================================
# def resend_otp(request):
#     from core.models import User

#     if request.method == 'POST':
#         email = request.POST.get('email', '').strip()

#         if request.session.get('otp_email') != email:
#             return JsonResponse({'success': False, 'error': 'Session mismatch.'})

#         try:
#             user = User.objects.get(email=email)
#         except User.DoesNotExist:
#             return JsonResponse({'success': False, 'error': 'User not found.'})

#         otp = ''.join(random.choices(string.digits, k=6))
#         user.otp            = otp
#         user.otp_created_at = timezone.now()
#         user.save(update_fields=['otp', 'otp_created_at'])

#         send_mail(
#             subject='Your VehicleVault Login OTP (Resent)',
#             message=f'Your new one-time password is: {otp}\n\nThis code expires in 5 minutes.',
#             from_email=settings.EMAIL_HOST_USER,
#             recipient_list=[email],
#             fail_silently=False,
#         )

#         return JsonResponse({'success': True})

#     return JsonResponse({'success': False})


# # ============================================================
# #  RESET PASSWORD VIEW  (AJAX POST from profile modal)
# # ============================================================
# def reset_password(request):
#     if not request.user.is_authenticated:
#         return JsonResponse({'success': False, 'error': 'Not authenticated.'})

#     if request.method == 'POST':
#         current  = request.POST.get('current_password', '')
#         new_pw1  = request.POST.get('new_password1', '')
#         new_pw2  = request.POST.get('new_password2', '')

#         # Verify current password
#         if not request.user.check_password(current):
#             return JsonResponse({'success': False, 'error': 'Current password is incorrect.'})

#         if new_pw1 != new_pw2:
#             return JsonResponse({'success': False, 'error': 'New passwords do not match.'})

#         if len(new_pw1) < 8:
#             return JsonResponse({'success': False, 'error': 'Password must be at least 8 characters.'})

#         # Set new password
#         request.user.set_password(new_pw1)

#         # Also store plain text if your model has raw_password field
#         if hasattr(request.user, 'raw_password'):
#             request.user.raw_password = new_pw1

#         request.user.save()

#         # Keep user logged in after password change
        
#         update_session_auth_hash(request, request.user)

#         return JsonResponse({'success': True})

#     return JsonResponse({'success': False, 'error': 'Invalid request.'})


# # ============================================================
# #  SIGNUP VIEW — save raw_password after creating user
# #  (add this block inside your existing signup view, after
# #   user = form.save(commit=False) ... user.save())
# # ============================================================
# #
# # def signup_view(request):
# #     ...
# #     if form.is_valid():
# #         user = form.save(commit=False)
# #         user.set_password(form.cleaned_data['password1'])
# #         if hasattr(user, 'raw_password'):
# #             user.raw_password = form.cleaned_data['password1']  # store plain text
# #         user.save()
# #         return redirect('login')
# #     ...

# # ============================================================
# #  ADD THIS VIEW to core/views.py
# #  (paste it before the userLogoutView function)
# # ============================================================

# def send_contact_email(request):
#     """
#     Receives the contact form POST via AJAX and sends an email
#     to the logged-in user's email address (same as OTP / welcome mail).
#     Returns JSON so the frontend can show success/error without page reload.
#     """
#     if request.method != 'POST':
#         return JsonResponse({'success': False, 'error': 'Invalid request method.'})

#     # Read form fields
#     fname   = request.POST.get('fname',   '').strip()
#     lname   = request.POST.get('lname',   '').strip()
#     email   = request.POST.get('email',   '').strip()
#     subject = request.POST.get('subject', '').strip()
#     message = request.POST.get('message', '').strip()

#     # Server-side validation (belt-and-suspenders alongside frontend validation)
#     if not all([fname, lname, email, subject, message]):
#         return JsonResponse({'success': False, 'error': 'All fields are required.'})

#     import re
#     if not re.match(r'^[^\s@]+@[^\s@]+\.[^\s@]+$', email):
#         return JsonResponse({'success': False, 'error': 'Please enter a valid email address.'})

#     try:
#         send_mail(
#             subject=f'[VehicleVault Contact] {subject}',
#             message=(
#                 f'New contact message from VehicleVault:\n\n'
#                 f'Name:    {fname} {lname}\n'
#                 f'Email:   {email}\n'
#                 f'Subject: {subject}\n\n'
#                 f'Message:\n{message}\n\n'
#                 f'---\nSent via the VehicleVault Contact page.'
#             ),
#             from_email=settings.EMAIL_HOST_USER,
#             recipient_list=[settings.EMAIL_HOST_USER],          # sends to site owner's inbox
#             fail_silently=False,
#         )
#         return JsonResponse({'success': True})

#     except Exception as e:
#         return JsonResponse({'success': False, 'error': f'Email could not be sent: {str(e)}'})


# def userLogoutView(request):
#     logout(request)
#     return redirect('login')

# def homeView(request):
#     return render(request, 'core/home.html')