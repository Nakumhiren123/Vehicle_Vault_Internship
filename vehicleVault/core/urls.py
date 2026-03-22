from django.contrib import admin
from django.urls import path,include
from . import views

urlpatterns = [
    path('', views.homeView, name='home'),
    path('signup/',views.userSignupView,name='signup'),
    path('login/',views.userLoginView,name='login'),
    path('logout/',views.userLogoutView,name='logout'),
    path('verify-otp/', views.verify_otp,  name='verify_otp'),
    path('resend-otp/', views.resend_otp,  name='resend_otp'),
    path('contact/send/', views.send_contact_email, name='send_contact_email'),

    # ── Password reset (AJAX from profile modal) ──
    path('user/reset-password/', views.reset_password, name='reset_password'),
      # Forgot password flow (3 steps)
    path('forgot-password/',          views.forgot_password,     name='forgot_password'),
    path('forgot-verify-otp/',        views.forgot_verify_otp,   name='forgot_verify_otp'),
    path('reset-password-form/',      views.reset_password_form, name='reset_password_form'),
]