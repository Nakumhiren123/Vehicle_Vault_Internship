from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .decorators import role_required
# Create your views here.
# @login_required(login_url='login')
@role_required(allowed_roles=['admin'])
def adminDashboardView(request):
    return render(request, 'compare/admin/admin_dashboard.html')

# @login_required(login_url='login')
@role_required(allowed_roles=['user'])
def userDashboardView(request):
    return render(request, 'compare/user/user_dashboard.html')