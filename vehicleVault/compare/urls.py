from django.urls import path
from django.http import HttpResponse
from . import views
urlpatterns = [
     path("test/", lambda request: HttpResponse("Compare Working")),
    path("admin/", views.adminDashboardView, name="admin-dashboard"),
    path("user/", views.userDashboardView, name="user-dashboard"),
    path('cars/', views.car_list, name='car_list'),
    path('cars/add/', views.car_create, name='car_create'),
    path('cars/edit/<int:pk>/', views.car_update, name='car_update'),
    path('cars/delete/<int:pk>/', views.car_delete, name='car_delete'),
    path('cars/public/', views.public_car_list, name='public_car_list'),
    path('cars/<int:pk>/', views.car_detail, name='car_detail'),
    path('review/delete/<int:pk>/', views.delete_review, name='delete_review'),
    path('cars/compare/', views.compare_cars, name='compare_cars'),
    path('admin/users/', views.admin_users_view, name='admin_users'),
    path('admin/reviews/', views.admin_reviews_view, name='admin_reviews'),
    path('admin/comparisons/', views.admin_comparisons_view, name='admin_comparisons'),
    path('admin/users/toggle/<int:user_id>/', views.toggle_user_status, name='toggle_user_status'),
    path('admin/analytics/', views.admin_analytics_view, name='admin_analytics'),
    # Footer Pages
    path('about/', views.about_page, name='about_page'),
    path('contact/', views.contact_page, name='contact_page'),
    path('privacy/', views.privacy_page, name='privacy_page'),
    path('terms/', views.terms_page, name='terms_page'),
    path('help/', views.help_page, name='help_page'),
    path('support/', views.support_page, name='support_page'),
    # path('admin/cars/', views.car_list, name='car_list'),
    # path('admin/cars/add/', views.car_create, name='car_create'),
    # path('admin/cars/edit/<int:pk>/', views.car_update, name='car_update'),
    # path('admin/cars/delete/<int:pk>/', views.car_delete, name='car_delete'),
]
