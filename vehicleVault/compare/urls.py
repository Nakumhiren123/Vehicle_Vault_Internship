from django.urls import path
from django.http import HttpResponse
from . import views
from django.http import JsonResponse
def devtools_json(request):
    return JsonResponse({})

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
    path('user/cars-viewed/', views.user_cars_viewed, name='user_cars_viewed'),
    path('user/comparisons/', views.user_comparisons, name='user_comparisons'),
    path('user/reviews/', views.user_reviews, name='user_reviews'),
    path('user/profile/',  views.user_profile,  name='user_profile'),
    path('admin/profile/',  views.admin_profile,  name='admin_profile'),
    path('.well-known/appspecific/com.chrome.devtools.json', devtools_json),
    path('user/wishlist', views.user_wishlist, name='user_wishlist'),
    # Footer Pages
    path('about/', views.about_page, name='about_page'),
    path('contact/', views.contact_page, name='contact_page'),
    path('privacy/', views.privacy_page, name='privacy_page'),
    path('terms/', views.terms_page, name='terms_page'),
    path('help/', views.help_page, name='help_page'),
    path('support/', views.support_page, name='support_page'),
    
    # Export CSV
    path('admin/export/cars/csv/',        views.export_cars_csv,        name='export_cars_csv'),
    path('admin/export/users/csv/',       views.export_users_csv,       name='export_users_csv'),
    path('admin/export/reviews/csv/',     views.export_reviews_csv,     name='export_reviews_csv'),
    path('admin/export/comparisons/csv/', views.export_comparisons_csv, name='export_comparisons_csv'),

    # User Comparison Export
    path('user/comparison/export/csv/', views.export_comparison_csv_user, name='export_comparison_csv_user'),
    path('user/comparison/export/pdf/', views.export_comparison_pdf_user, name='export_comparison_pdf_user'),
 
    # Export PDF
    path('admin/export/cars/pdf/',        views.export_cars_pdf,        name='export_cars_pdf'),
    path('admin/export/users/pdf/',       views.export_users_pdf,       name='export_users_pdf'),
    path('admin/export/reviews/pdf/',     views.export_reviews_pdf,     name='export_reviews_pdf'),
    path('admin/export/comparisons/pdf/', views.export_comparisons_pdf, name='export_comparisons_pdf'),

    # Car Variant Management
    path('admin/cars/<int:car_pk>/variants/',                 views.variant_list,   name='variant_list'),
    path('admin/cars/<int:car_pk>/variants/add/',             views.variant_create, name='variant_create'),
    path('admin/cars/<int:car_pk>/variants/edit/<int:pk>/',   views.variant_update, name='variant_update'),
    path('admin/cars/<int:car_pk>/variants/delete/<int:pk>/', views.variant_delete, name='variant_delete'),

    # Accessory Management
    path('admin/accessories/',                views.accessory_list,   name='accessory_list'),
    path('admin/accessories/add/',            views.accessory_create, name='accessory_create'),
    path('admin/accessories/edit/<int:pk>/',  views.accessory_update, name='accessory_update'),
    path('admin/accessories/delete/<int:pk>/',views.accessory_delete, name='accessory_delete'),

    # Car Battle / Voting
    path('user/battles/',                          views.battle_list,    name='battle_list'),
    path('user/battles/vote/<int:battle_id>/<int:choice>/', views.battle_vote, name='battle_vote'),
    path('admin/battles/',                         views.admin_battles,  name='admin_battles'),
    path('admin/battles/create/',                  views.battle_create,  name='battle_create'),
    path('admin/battles/<int:battle_id>/toggle/',  views.battle_toggle,  name='battle_toggle'),
    
    # path('admin/cars/', views.car_list, name='car_list'),
    # path('admin/cars/add/', views.car_create, name='car_create'),
    # path('admin/cars/edit/<int:pk>/', views.car_update, name='car_update'),
    # path('admin/cars/delete/<int:pk>/', views.car_delete, name='car_delete'),
]