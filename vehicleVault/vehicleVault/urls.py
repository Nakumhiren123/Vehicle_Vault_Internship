from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect
from django.conf import settings
from django.conf.urls.static import static
from django.http import HttpResponseRedirect

# Customise Django admin panel branding
admin.site.site_header  = "VehicleVault Admin"
admin.site.site_title   = "VehicleVault"
admin.site.index_title  = "Welcome to VehicleVault Admin Panel"

# After Django admin login → redirect to custom admin dashboard
from django.contrib.admin import AdminSite

def _to_custom_admin(self, request, *args, **kwargs):
    if request.user.is_authenticated:
        role = getattr(request.user, 'role', '')
        if role == 'admin' or request.user.is_staff or request.user.is_superuser:
            return HttpResponseRedirect('/compare/admin/')
        return HttpResponseRedirect('/compare/user/')
    return HttpResponseRedirect('/login/')

AdminSite.index     = _to_custom_admin
AdminSite.app_index = _to_custom_admin

urlpatterns = [
    path('django-admin/', admin.site.urls),
    path('admin/', lambda r: (
        HttpResponseRedirect('/compare/admin/')
        if r.user.is_authenticated and (
            getattr(r.user, 'role', '') == 'admin' or r.user.is_staff or r.user.is_superuser
        )
        else HttpResponseRedirect('/compare/user/')
        if r.user.is_authenticated
        else HttpResponseRedirect('/login/')
    )),
    path('', include('core.urls')),
    path('compare/', include('compare.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    