from django.urls import path
from . import views
urlpatterns = [
    path("admin/", views.adminDashboardView, name="admin-dashboard"),
    path("user/", views.userDashboardView, name="user-dashboard"),
]
