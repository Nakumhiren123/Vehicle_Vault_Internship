from django.shortcuts import render, redirect, get_object_or_404
# Create your views here.
from django.contrib.auth.decorators import login_required, user_passes_test
from .decorators import role_required
from .models import Car, Review,Comparison
from .forms import CarForm, ReviewForm
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Avg, Count
from core.models import User
from django.db.models.functions import TruncMonth
from django.utils import timezone 
from datetime import timedelta
from .models import UserInteraction
from django.core.paginator import Paginator
from django.db.models import Q

# @login_required(login_url='login')
@role_required(allowed_roles=['admin'])
# def adminDashboardView(request):
#     return render(request, 'compare/admin/admin_dashboard.html')
def adminDashboardView(request):

    from .models import Comparison, UserInteraction
    from django.db.models import Count, Avg

    total_cars = Car.objects.count()
    active_cars = Car.objects.filter(status=True).count()
    total_users = User.objects.count()
    total_reviews = Review.objects.count()
    total_comparisons = Comparison.objects.count()

    # Most Reviewed Cars
    top_reviewed = (
        Review.objects
        .values('car__carName')
        .annotate(total=Count('car'))
        .order_by('-total')[:5]
    )

    # Most Compared Cars
    top_compared = (
        Comparison.objects
        .values('car1__carName')
        .annotate(total=Count('car1'))
        .order_by('-total')[:5]
    )

    # Most Active Users (by comparisons)
    active_users = (
        Comparison.objects
        .values('user__email')
        .annotate(total=Count('user'))
        .order_by('-total')[:5]
    )

    context = {
        "total_cars": total_cars,
        "active_cars": active_cars,
        "total_users": total_users,
        "total_reviews": total_reviews,
        "total_comparisons": total_comparisons,
        "top_reviewed": top_reviewed,
        "top_compared": top_compared,
        "active_users": active_users,
    }

    return render(request, 'compare/admin/admin_dashboard.html', context)

@role_required(allowed_roles=['admin'])
def admin_users_view(request):

    users = User.objects.all().annotate(
        total_reviews=Count('review'),
        total_comparisons=Count('comparison')
    )

    return render(request, 'compare/admin/admin_users.html', {
        'users': users
    })

@role_required(allowed_roles=['admin'])
def toggle_user_status(request, user_id):
    user = User.objects.get(id=user_id)
    user.is_active = not user.is_active
    user.save()
    return redirect('admin_users')

@role_required(allowed_roles=['admin'])
def admin_reviews_view(request):

    reviews = Review.objects.select_related('car', 'user').order_by('-createdAt')

    return render(request, 'compare/admin/admin_reviews.html', {
        'reviews': reviews
    })
 
@role_required(allowed_roles=['admin'])
def admin_comparisons_view(request):

    comparisons = Comparison.objects.select_related(
        'user', 'car1', 'car2'
    ).order_by('-comparedAt')

    return render(request, 'compare/admin/admin_comparisons.html', {
        'comparisons': comparisons
    })   


@role_required(allowed_roles=['admin'])
def admin_analytics_view(request):

    from .models import Comparison, Review
    from core.models import User
    from .models import Car

    # 1️⃣ Monthly Comparisons (last 6 months)
    six_months_ago = now() - timedelta(days=180)

    monthly_comparisons = (
        Comparison.objects
        .filter(comparedAt__gte=six_months_ago)
        .annotate(month=TruncMonth('comparedAt'))
        .values('month')
        .annotate(total=Count('id'))
        .order_by('month')
    )

    comp_labels = [m['month'].strftime("%b %Y") for m in monthly_comparisons]
    comp_data = [m['total'] for m in monthly_comparisons]

    # 2️⃣ Monthly User Registrations
    monthly_users = (
        User.objects
        .filter(created_at__gte=six_months_ago)
        .annotate(month=TruncMonth('created_at'))
        .values('month')
        .annotate(total=Count('id'))
        .order_by('month')
    )

    user_labels = [m['month'].strftime("%b %Y") for m in monthly_users]
    user_data = [m['total'] for m in monthly_users]

    # 3️⃣ Most Reviewed Cars
    top_reviewed = (
        Review.objects
        .values('car__carName')
        .annotate(total=Count('id'))
        .order_by('-total')[:5]
    )

    review_labels = [r['car__carName'] for r in top_reviewed]
    review_data = [r['total'] for r in top_reviewed]

    # 4️⃣ Fuel Type Distribution
    fuel_distribution = (
        Car.objects
        .values('fuelType')
        .annotate(total=Count('id'))
    )

    fuel_labels = [f['fuelType'] for f in fuel_distribution]
    fuel_data = [f['total'] for f in fuel_distribution]

    context = {
        "comp_labels": comp_labels,
        "comp_data": comp_data,
        "user_labels": user_labels,
        "user_data": user_data,
        "review_labels": review_labels,
        "review_data": review_data,
        "fuel_labels": fuel_labels,
        "fuel_data": fuel_data,
    }

    return render(request, 'compare/admin/admin_analytics.html', context)

# @login_required(login_url='login')
@role_required(allowed_roles=['user'])
def userDashboardView(request):
    recent_cars = Car.objects.filter(status=True)[:4]

    context = {
        "recent_cars": recent_cars,
        "cars_viewed": 5,
        "comparisons": 2,
        "reviews": 3
    }
    return render(request, 'compare/user/user_dashboard.html')





@role_required(allowed_roles=['admin'])
def car_list(request):

    search_query = request.GET.get('search')

    cars = Car.objects.all().order_by('id')

    if search_query:
        cars = cars.filter(carName__icontains=search_query)

    paginator = Paginator(cars, 5)
    page_number = request.GET.get('page')
    cars = paginator.get_page(page_number)

    brand_filter = request.GET.get('brand')

    if brand_filter:
        cars = cars.filter(brand__icontains=brand_filter)

    return render(request, 'compare/admin/car_list.html', {
        'cars': cars,
        'search_query': search_query
    })

# def public_car_list(request):
#     cars = Car.objects.filter(status=True).order_by('id')
#     return render(request, 'compare/user/car_list.html', {'cars':cars})
def public_car_list(request):
    search = request.GET.get('search', '').strip()
    
    cars = Car.objects.all()
    
    if search:
        cars = cars.filter(
            Q(carName__icontains=search) |
            Q(brand__icontains=search)   |
            Q(fuelType__icontains=search)
        )
    
    return render(request, 'compare/user/car_list.html', {
        'cars': cars,
        'search': search,   # pass it back so input stays filled
    })

@role_required(allowed_roles=['admin'])
def car_create(request):
    form = CarForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        form.save()
        return redirect('car_list')
    return render(request, 'compare/admin/car_form.html', {'form': form})


@role_required(allowed_roles=['admin'])
def car_update(request, pk):
    car = get_object_or_404(Car, pk=pk)
    form = CarForm(request.POST or None, request.FILES or None, instance=car)

    if request.method == "POST":
        print("FILES:", request.FILES)   # DEBUG LINE

    if form.is_valid():
        form.save()
        print("SAVED SUCCESSFULLY")     # DEBUG LINE
        return redirect('car_list')

    return render(request, 'compare/admin/car_form.html', {'form': form})


@role_required(allowed_roles=['admin'])
def car_delete(request, pk):
    car = get_object_or_404(Car, pk=pk)
    car.delete()
    return redirect('car_list')





def car_detail(request, pk):

    car = get_object_or_404(Car, pk=pk)
    if request.user.is_authenticated:
        UserInteraction.objects.create(
            user=request.user,
            car=car,
            interactionType="view",
            interactionDate=timezone.now().date()  # ← this line fixes the error
        )
    reviews = Review.objects.filter(car=car).order_by('-createdAt')

    average_rating = reviews.aggregate(avg=Avg('rating'))['avg']
    average_rating = round(average_rating, 1) if average_rating else 0

    form = ReviewForm()

    if request.method == "POST":
        if request.user.is_authenticated:

            # Restrict 1 review per user
            if Review.objects.filter(car=car, user=request.user).exists():
                return redirect('car_detail', pk=car.id)

            form = ReviewForm(request.POST)
            if form.is_valid():
                review = form.save(commit=False)
                review.car = car
                review.user = request.user
                review.save()
                return redirect('car_detail', pk=car.id)

    return render(request, 'compare/user/car_detail.html', {
        'car': car,
        'reviews': reviews,
        'form': form,
        'average_rating': average_rating
    })

@staff_member_required
def delete_review(request, pk):
    review = get_object_or_404(Review, pk=pk)
    car_id = review.car.id
    review.delete()
    return redirect('car_detail', pk=car_id)

def compare_cars(request):
    car_ids = request.GET.getlist('cars')
    if len(car_ids) < 2:
        return redirect('public_car_list')
    print("Selected IDs:", car_ids)  # DEBUG

    cars = Car.objects.filter(id__in=car_ids)

    comparison_data = []

    for car in cars:
        avg_rating = Review.objects.filter(car=car).aggregate(
            Avg('rating')
        )['rating__avg'] or 0

        comparison_data.append({
            'car': car,
            'avg_rating': round(avg_rating, 1)
        })

    return render(request, 'compare/user/compare.html', {
        'comparison_data': comparison_data
    })



@login_required
def user_cars_viewed(request):

    interactions = UserInteraction.objects.filter(
        user=request.user,
        interactionType="view"
    ).select_related("car")

    context = {
        "interactions": interactions
    }

    return render(request, "compare/user/cars_viewed.html", context)

@login_required
def user_comparisons(request):

    comparisons = Comparison.objects.filter(user=request.user).order_by('-comparedAt')

    context = {
        "comparisons": comparisons
    }

    return render(request, "compare/user/user_comparisons.html", context)

# @login_required
# def user_reviews(request):

#     reviews = Review.objects.filter(user=request.user).order_by('-createdAt')

#     context = {
#         "reviews": reviews
#     }

#     return render(request, "compare/user/user_reviews.html", context)
@login_required
def user_reviews(request):
    reviews = Review.objects.filter(user=request.user).order_by('-createdAt')
    return render(request, 'compare/user/user_reviews.html', {
        'reviews': reviews,
    })
@login_required
def user_profile(request):
    cars_viewed  = UserInteraction.objects.filter(user=request.user, interactionType='view').count()
    comparisons  = Comparison.objects.filter(user=request.user).count()
    reviews      = Review.objects.filter(user=request.user).count()
    return render(request, 'compare/user/user_profile.html', {
        'cars_viewed': cars_viewed,
        'comparisons': comparisons,
        'reviews':     reviews,
    })


# ==============================
# Footer Static Pages
# ==============================

def about_page(request):
    return render(request, 'compare/static_pages/about.html')

def contact_page(request):
    return render(request, 'compare/static_pages/contact.html')

def privacy_page(request):
    return render(request, 'compare/static_pages/privacy.html')

def terms_page(request):
    return render(request, 'compare/static_pages/terms.html')

def help_page(request):
    return render(request, 'compare/static_pages/help.html')

def support_page(request):
    return render(request, 'compare/static_pages/support.html')