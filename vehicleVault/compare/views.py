from django.shortcuts import render
from django.contrib.auth.decorators import login_required

# Create your views here.
@login_required(login_url='login')
def adminDashboardView(request):
    return render(request, 'compare/admin_dashboard.html')

@login_required(login_url='login')
def userDashboardView(request):
    return render(request, 'compare/user_dashboard.html')