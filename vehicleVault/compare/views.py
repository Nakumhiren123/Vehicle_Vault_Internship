from django.shortcuts import render, redirect, get_object_or_404
# Create your views here.
from django.contrib.auth.decorators import login_required, user_passes_test
from .decorators import role_required
from .models import Car, Review, Comparison, SearchHistory, Accessory, CarAccessoryMapping, CarVariant, Wishlist
from .forms import CarForm, ReviewForm, AccessoryForm, CarVariantForm, CarVariantFormSet
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Avg, Count
from core.models import User
from django.db.models.functions import TruncMonth
from django.utils import timezone 
# from django.utils.timezone import now
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


    # 1️⃣ Monthly Comparisons (last 6 months)
    six_months_ago = timezone.now() - timedelta(days=180)

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
    from .models import Car, Review, Comparison, UserPreference, SearchHistory, UserInteraction

    # ── Core stats (used by activity cards) ──────────────────
    cars_viewed = UserInteraction.objects.filter(
        user=request.user, interactionType='view'
    ).count()

    comparisons = Comparison.objects.filter(user=request.user).count()

    reviews = Review.objects.filter(user=request.user).count()

    wishlist_count = Wishlist.objects.filter(user=request.user).count()

    # ── Featured cars (6 most recent active cars) ────────────
    recent_cars = Car.objects.filter(status=True).order_by('-id')[:6]

    # ── User preferences (UserPreference model) ──────────────
    try:
        user_preference = UserPreference.objects.get(user=request.user)
    except UserPreference.DoesNotExist:
        user_preference = None

    # ── Recent comparisons (Comparison model) ────────────────
    recent_comparisons = Comparison.objects.filter(
        user=request.user
    ).select_related('car1', 'car2').order_by('-comparedAt')[:4]

    # ── Recent search history (SearchHistory model) ──────────
    recent_searches = SearchHistory.objects.filter(
        user=request.user
    ).order_by('-searchedAt')[:8]

    # ── My recent reviews (Review model) ─────────────────────
    my_reviews = Review.objects.filter(
        user=request.user
    ).select_related('car').order_by('-createdAt')[:3]

    context = {
        'cars_viewed':        cars_viewed,
        'comparisons':        comparisons,
        'reviews':            reviews,
        'wishlist_count':     wishlist_count,
        'recent_cars':        recent_cars,
        'user_preference':    user_preference,
        'recent_comparisons': recent_comparisons,
        'recent_searches':    recent_searches,
        'my_reviews':         my_reviews,
    }

    return render(request, 'compare/user/user_dashboard.html', context)





@role_required(allowed_roles=['admin'])
def car_list(request):
    search_query  = request.GET.get('search', '').strip()
    fuel_filter   = request.GET.get('fuel', '').strip()
    brand_filter  = request.GET.get('brand', '').strip()
    trans_filter  = request.GET.get('transmission', '').strip()
    status_filter = request.GET.get('status', '').strip()
    sort          = request.GET.get('sort', '').strip()

    cars = Car.objects.all()

    # All filters BEFORE pagination
    if search_query:
        cars = cars.filter(
            Q(carName__icontains=search_query) |
            Q(brand__icontains=search_query)
        )
    if fuel_filter:
        cars = cars.filter(fuelType__iexact=fuel_filter)
    if brand_filter:
        cars = cars.filter(brand__iexact=brand_filter)
    if trans_filter:
        cars = cars.filter(transmission__iexact=trans_filter)
    if status_filter == 'active':
        cars = cars.filter(status=True)
    elif status_filter == 'inactive':
        cars = cars.filter(status=False)

    sort_map = {
        'price_asc': 'price', 'price_desc': '-price',
        'mileage': '-mileage', 'newest': '-launchYear', 'name': 'carName',
    }
    cars = cars.order_by(sort_map.get(sort, 'id'))

    all_cars      = Car.objects.all()
    fuel_types    = all_cars.values_list('fuelType', flat=True).distinct().order_by('fuelType')
    brands        = all_cars.values_list('brand', flat=True).distinct().order_by('brand')
    transmissions = all_cars.values_list('transmission', flat=True).distinct().order_by('transmission')
    total_filtered = cars.count()
    active_count   = Car.objects.filter(status=True).count()
    inactive_count = Car.objects.filter(status=False).count()

    paginator   = Paginator(cars, 8)
    page_number = request.GET.get('page')
    cars        = paginator.get_page(page_number)

    return render(request, 'compare/admin/car_list.html', {
        'cars':           cars,
        'total_filtered': total_filtered,
        'active_count':   active_count,
        'inactive_count': inactive_count,
        'search_query':   search_query,
        'sel_fuel':       fuel_filter,
        'sel_brand':      brand_filter,
        'sel_trans':      trans_filter,
        'sel_status':     status_filter,
        'sel_sort':       sort,
        'fuel_types':     fuel_types,
        'brands':         brands,
        'transmissions':  transmissions,
    })

# def public_car_list(request):
#     cars = Car.objects.filter(status=True).order_by('id')
#     return render(request, 'compare/user/car_list.html', {'cars':cars})
def public_car_list(request):
    search     = request.GET.get('search',       '').strip()
    sel_fuel   = request.GET.get('fuel',         '').strip()
    sel_brand  = request.GET.get('brand',        '').strip()
    sel_trans  = request.GET.get('transmission', '').strip()
    sel_sort   = request.GET.get('sort',         '').strip()

    cars = Car.objects.filter(status=True)

    # ── Filters ───────────────────────────────────────────────
    if search:
        cars = cars.filter(
            Q(carName__icontains=search) |
            Q(brand__icontains=search)   |
            Q(fuelType__icontains=search)
        )
    if sel_fuel:
        cars = cars.filter(fuelType__iexact=sel_fuel)
    if sel_brand:
        cars = cars.filter(brand__iexact=sel_brand)
    if sel_trans:
        cars = cars.filter(transmission__iexact=sel_trans)

    # ── Sorting ───────────────────────────────────────────────
    sort_map = {
        'price_asc':  'price',
        'price_desc': '-price',
        'mileage':    '-mileage',
        'newest':     '-launchYear',
        'oldest':     'launchYear',
    }
    cars = cars.order_by(sort_map.get(sel_sort, 'id'))

    # ── Dropdown options (from all active cars) ───────────────
    all_cars      = Car.objects.filter(status=True)
    fuel_types    = all_cars.values_list('fuelType',      flat=True).distinct().order_by('fuelType')
    brands        = all_cars.values_list('brand',         flat=True).distinct().order_by('brand')
    transmissions = all_cars.values_list('transmission',  flat=True).distinct().order_by('transmission')

    # ── Brand picker data (brand + car count) ──────────────────
    from django.db.models import Count
    brand_data = (
        all_cars.values('brand')
        .annotate(car_count=Count('id'))
        .order_by('brand')
    )

    # Pass wishlist IDs so heart buttons show correct state
    wishlist_ids = set()
    if request.user.is_authenticated:
        wishlist_ids = set(Wishlist.objects.filter(user=request.user).values_list('car_id', flat=True))

    return render(request, 'compare/user/car_list.html', {
        'cars':          cars,
        'search':        search,
        'sel_fuel':      sel_fuel,
        'sel_brand':     sel_brand,
        'sel_trans':     sel_trans,
        'sel_sort':      sel_sort,
        'fuel_types':    fuel_types,
        'brands':        brands,
        'transmissions': transmissions,
        'wishlist_ids':  wishlist_ids,
        'brand_data':    brand_data,
        'sel_brand':     sel_brand,
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

    is_wishlisted = False
    if request.user.is_authenticated:
        is_wishlisted = Wishlist.objects.filter(user=request.user, car=car).exists()

    return render(request, 'compare/user/car_detail.html', {
        'car':            car,
        'reviews':        reviews,
        'form':           form,
        'average_rating': average_rating,
        'is_wishlisted':  is_wishlisted,
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

    cars = list(Car.objects.filter(id__in=car_ids))

    # ── Save comparison to DB (only for logged-in users) ──────
    if request.user.is_authenticated and len(cars) >= 2:
        Comparison.objects.create(
            user=request.user,
            car1=cars[0],
            car2=cars[1],
        )

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
    comparisons = Comparison.objects.filter(
        user=request.user
    ).select_related('car1', 'car2').order_by('-comparedAt')

    return render(request, "compare/user/user_comparisons.html", {
        "comparisons": comparisons
    })

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
@login_required
def admin_profile(request):
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



# from django.shortcuts import render, redirect, get_object_or_404
# # Create your views here.
# from django.contrib.auth.decorators import login_required, user_passes_test
# from .decorators import role_required
# from .models import Car, Review, Comparison, SearchHistory, Accessory, CarAccessoryMapping, CarVariant, Wishlist
# from .forms import CarForm, ReviewForm, AccessoryForm, CarVariantForm, CarVariantFormSet
# from django.contrib.admin.views.decorators import staff_member_required
# from django.db.models import Avg, Count
# from core.models import User
# from django.db.models.functions import TruncMonth
# from django.utils import timezone 
# # from django.utils.timezone import now
# from datetime import timedelta
# from .models import UserInteraction
# from django.core.paginator import Paginator
# from django.db.models import Q


# # @login_required(login_url='login')
# @role_required(allowed_roles=['admin'])
# # def adminDashboardView(request):
# #     return render(request, 'compare/admin/admin_dashboard.html')
# def adminDashboardView(request):

#     from .models import Comparison, UserInteraction
#     from django.db.models import Count, Avg

#     total_cars = Car.objects.count()
#     active_cars = Car.objects.filter(status=True).count()
#     total_users = User.objects.count()
#     total_reviews = Review.objects.count()
#     total_comparisons = Comparison.objects.count()

#     # Most Reviewed Cars
#     top_reviewed = (
#         Review.objects
#         .values('car__carName')
#         .annotate(total=Count('car'))
#         .order_by('-total')[:5]
#     )

#     # Most Compared Cars
#     top_compared = (
#         Comparison.objects
#         .values('car1__carName')
#         .annotate(total=Count('car1'))
#         .order_by('-total')[:5]
#     )

#     # Most Active Users (by comparisons)
#     active_users = (
#         Comparison.objects
#         .values('user__email')
#         .annotate(total=Count('user'))
#         .order_by('-total')[:5]
#     )

#     context = {
#         "total_cars": total_cars,
#         "active_cars": active_cars,
#         "total_users": total_users,
#         "total_reviews": total_reviews,
#         "total_comparisons": total_comparisons,
#         "top_reviewed": top_reviewed,
#         "top_compared": top_compared,
#         "active_users": active_users,
#     }

#     return render(request, 'compare/admin/admin_dashboard.html', context)

# @role_required(allowed_roles=['admin'])
# def admin_users_view(request):

#     users = User.objects.all().annotate(
#         total_reviews=Count('review'),
#         total_comparisons=Count('comparison')
#     )

#     return render(request, 'compare/admin/admin_users.html', {
#         'users': users
#     })

# @role_required(allowed_roles=['admin'])
# def toggle_user_status(request, user_id):
#     user = User.objects.get(id=user_id)
#     user.is_active = not user.is_active
#     user.save()
#     return redirect('admin_users')

# @role_required(allowed_roles=['admin'])
# def admin_reviews_view(request):

#     reviews = Review.objects.select_related('car', 'user').order_by('-createdAt')

#     return render(request, 'compare/admin/admin_reviews.html', {
#         'reviews': reviews
#     })
 
# @role_required(allowed_roles=['admin'])
# def admin_comparisons_view(request):

#     comparisons = Comparison.objects.select_related(
#         'user', 'car1', 'car2'
#     ).order_by('-comparedAt')

#     return render(request, 'compare/admin/admin_comparisons.html', {
#         'comparisons': comparisons
#     })   


# @role_required(allowed_roles=['admin'])
# def admin_analytics_view(request):


#     # 1️⃣ Monthly Comparisons (last 6 months)
#     six_months_ago = timezone.now() - timedelta(days=180)

#     monthly_comparisons = (
#         Comparison.objects
#         .filter(comparedAt__gte=six_months_ago)
#         .annotate(month=TruncMonth('comparedAt'))
#         .values('month')
#         .annotate(total=Count('id'))
#         .order_by('month')
#     )

#     comp_labels = [m['month'].strftime("%b %Y") for m in monthly_comparisons]
#     comp_data = [m['total'] for m in monthly_comparisons]

#     # 2️⃣ Monthly User Registrations
#     monthly_users = (
#         User.objects
#         .filter(created_at__gte=six_months_ago)
#         .annotate(month=TruncMonth('created_at'))
#         .values('month')
#         .annotate(total=Count('id'))
#         .order_by('month')
#     )

#     user_labels = [m['month'].strftime("%b %Y") for m in monthly_users]
#     user_data = [m['total'] for m in monthly_users]

#     # 3️⃣ Most Reviewed Cars
#     top_reviewed = (
#         Review.objects
#         .values('car__carName')
#         .annotate(total=Count('id'))
#         .order_by('-total')[:5]
#     )

#     review_labels = [r['car__carName'] for r in top_reviewed]
#     review_data = [r['total'] for r in top_reviewed]

#     # 4️⃣ Fuel Type Distribution
#     fuel_distribution = (
#         Car.objects
#         .values('fuelType')
#         .annotate(total=Count('id'))
#     )

#     fuel_labels = [f['fuelType'] for f in fuel_distribution]
#     fuel_data = [f['total'] for f in fuel_distribution]

#     context = {
#         "comp_labels": comp_labels,
#         "comp_data": comp_data,
#         "user_labels": user_labels,
#         "user_data": user_data,
#         "review_labels": review_labels,
#         "review_data": review_data,
#         "fuel_labels": fuel_labels,
#         "fuel_data": fuel_data,
#     }

#     return render(request, 'compare/admin/admin_analytics.html', context)

# # @login_required(login_url='login')
# @role_required(allowed_roles=['user'])
# def userDashboardView(request):
#     from .models import Car, Review, Comparison, UserPreference, SearchHistory, UserInteraction

#     # ── Core stats (used by activity cards) ──────────────────
#     cars_viewed = UserInteraction.objects.filter(
#         user=request.user, interactionType='view'
#     ).count()

#     comparisons = Comparison.objects.filter(user=request.user).count()

#     reviews = Review.objects.filter(user=request.user).count()

#     # ── Featured cars (6 most recent active cars) ────────────
#     recent_cars = Car.objects.filter(status=True).order_by('-id')[:6]

#     # ── User preferences (UserPreference model) ──────────────
#     try:
#         user_preference = UserPreference.objects.get(user=request.user)
#     except UserPreference.DoesNotExist:
#         user_preference = None

#     # ── Recent comparisons (Comparison model) ────────────────
#     recent_comparisons = Comparison.objects.filter(
#         user=request.user
#     ).select_related('car1', 'car2').order_by('-comparedAt')[:4]

#     # ── Recent search history (SearchHistory model) ──────────
#     recent_searches = SearchHistory.objects.filter(
#         user=request.user
#     ).order_by('-searchedAt')[:8]

#     # ── My recent reviews (Review model) ─────────────────────
#     my_reviews = Review.objects.filter(
#         user=request.user
#     ).select_related('car').order_by('-createdAt')[:3]

#     context = {
#         'cars_viewed':        cars_viewed,
#         'comparisons':        comparisons,
#         'reviews':            reviews,
#         'recent_cars':        recent_cars,
#         'user_preference':    user_preference,
#         'recent_comparisons': recent_comparisons,
#         'recent_searches':    recent_searches,
#         'my_reviews':         my_reviews,
#     }

#     return render(request, 'compare/user/user_dashboard.html', context)





# @role_required(allowed_roles=['admin'])
# def car_list(request):

#     search_query = request.GET.get('search')

#     cars = Car.objects.all().order_by('id')

#     if search_query:
#         cars = cars.filter(carName__icontains=search_query)

#     paginator = Paginator(cars, 5)
#     page_number = request.GET.get('page')
#     cars = paginator.get_page(page_number)

#     brand_filter = request.GET.get('brand')

#     if brand_filter:
#         cars = cars.filter(brand__icontains=brand_filter)

#     return render(request, 'compare/admin/car_list.html', {
#         'cars': cars,
#         'search_query': search_query
#     })

# # def public_car_list(request):
# #     cars = Car.objects.filter(status=True).order_by('id')
# #     return render(request, 'compare/user/car_list.html', {'cars':cars})
# def public_car_list(request):
#     search = request.GET.get('search', '').strip()
    
#     cars = Car.objects.all()
    
#     if search:
#         cars = cars.filter(
#             Q(carName__icontains=search) |
#             Q(brand__icontains=search)   |
#             Q(fuelType__icontains=search)
#         )
    
#     return render(request, 'compare/user/car_list.html', {
#         'cars': cars,
#         'search': search,   # pass it back so input stays filled
#     })

# @role_required(allowed_roles=['admin'])
# def car_create(request):
#     form = CarForm(request.POST or None, request.FILES or None)
#     if form.is_valid():
#         form.save()
#         return redirect('car_list')
#     return render(request, 'compare/admin/car_form.html', {'form': form})


# @role_required(allowed_roles=['admin'])
# def car_update(request, pk):
#     car = get_object_or_404(Car, pk=pk)
#     form = CarForm(request.POST or None, request.FILES or None, instance=car)

#     if request.method == "POST":
#         print("FILES:", request.FILES)   # DEBUG LINE

#     if form.is_valid():
#         form.save()
#         print("SAVED SUCCESSFULLY")     # DEBUG LINE
#         return redirect('car_list')

#     return render(request, 'compare/admin/car_form.html', {'form': form})


# @role_required(allowed_roles=['admin'])
# def car_delete(request, pk):
#     car = get_object_or_404(Car, pk=pk)
#     car.delete()
#     return redirect('car_list')





# def car_detail(request, pk):

#     car = get_object_or_404(Car, pk=pk)
#     if request.user.is_authenticated:
#         UserInteraction.objects.create(
#             user=request.user,
#             car=car,
#             interactionType="view",
#             interactionDate=timezone.now().date()  # ← this line fixes the error
#         )
#     reviews = Review.objects.filter(car=car).order_by('-createdAt')

#     average_rating = reviews.aggregate(avg=Avg('rating'))['avg']
#     average_rating = round(average_rating, 1) if average_rating else 0

#     form = ReviewForm()

#     if request.method == "POST":
#         if request.user.is_authenticated:

#             # Restrict 1 review per user
#             if Review.objects.filter(car=car, user=request.user).exists():
#                 return redirect('car_detail', pk=car.id)

#             form = ReviewForm(request.POST)
#             if form.is_valid():
#                 review = form.save(commit=False)
#                 review.car = car
#                 review.user = request.user
#                 review.save()
#                 return redirect('car_detail', pk=car.id)

#     return render(request, 'compare/user/car_detail.html', {
#         'car': car,
#         'reviews': reviews,
#         'form': form,
#         'average_rating': average_rating
#     })

# @staff_member_required
# def delete_review(request, pk):
#     review = get_object_or_404(Review, pk=pk)
#     car_id = review.car.id
#     review.delete()
#     return redirect('car_detail', pk=car_id)

# def compare_cars(request):
#     car_ids = request.GET.getlist('cars')
#     if len(car_ids) < 2:
#         return redirect('public_car_list')
#     print("Selected IDs:", car_ids)  # DEBUG

#     cars = Car.objects.filter(id__in=car_ids)

#     comparison_data = []

#     for car in cars:
#         avg_rating = Review.objects.filter(car=car).aggregate(
#             Avg('rating')
#         )['rating__avg'] or 0

#         comparison_data.append({
#             'car': car,
#             'avg_rating': round(avg_rating, 1)
#         })

#     return render(request, 'compare/user/compare.html', {
#         'comparison_data': comparison_data
#     })



# @login_required
# def user_cars_viewed(request):

#     interactions = UserInteraction.objects.filter(
#         user=request.user,
#         interactionType="view"
#     ).select_related("car")

#     context = {
#         "interactions": interactions
#     }

#     return render(request, "compare/user/cars_viewed.html", context)

# @login_required
# def user_comparisons(request):

#     comparisons = Comparison.objects.filter(user=request.user).order_by('-comparedAt')

#     context = {
#         "comparisons": comparisons
#     }

#     return render(request, "compare/user/user_comparisons.html", context)

# # @login_required
# # def user_reviews(request):

# #     reviews = Review.objects.filter(user=request.user).order_by('-createdAt')

# #     context = {
# #         "reviews": reviews
# #     }

# #     return render(request, "compare/user/user_reviews.html", context)
# @login_required
# def user_reviews(request):
#     reviews = Review.objects.filter(user=request.user).order_by('-createdAt')
#     return render(request, 'compare/user/user_reviews.html', {
#         'reviews': reviews,
#     })
# @login_required
# def user_profile(request):
#     cars_viewed  = UserInteraction.objects.filter(user=request.user, interactionType='view').count()
#     comparisons  = Comparison.objects.filter(user=request.user).count()
#     reviews      = Review.objects.filter(user=request.user).count()
#     return render(request, 'compare/user/user_profile.html', {
#         'cars_viewed': cars_viewed,
#         'comparisons': comparisons,
#         'reviews':     reviews,
#     })
# @login_required
# def admin_profile(request):
#     cars_viewed  = UserInteraction.objects.filter(user=request.user, interactionType='view').count()
#     comparisons  = Comparison.objects.filter(user=request.user).count()
#     reviews      = Review.objects.filter(user=request.user).count()
#     return render(request, 'compare/user/user_profile.html', {
#         'cars_viewed': cars_viewed,
#         'comparisons': comparisons,
#         'reviews':     reviews,
#     })


# # ==============================
# # Footer Static Pages
# # ==============================

# def about_page(request):
#     return render(request, 'compare/static_pages/about.html')

# def contact_page(request):
#     return render(request, 'compare/static_pages/contact.html')

# def privacy_page(request):
#     return render(request, 'compare/static_pages/privacy.html')

# def terms_page(request):
#     return render(request, 'compare/static_pages/terms.html')

# def help_page(request):
#     return render(request, 'compare/static_pages/help.html')

# def support_page(request):
#     return render(request, 'compare/static_pages/support.html')

# ============================================================
#  ACCESSORY MANAGEMENT (Admin)
# ============================================================

@role_required(allowed_roles=['admin'])
def accessory_list(request):
    search = request.GET.get('search', '').strip()
    type_filter = request.GET.get('type', '').strip()

    accessories = Accessory.objects.all()

    if search:
        accessories = accessories.filter(
            Q(accessoryName__icontains=search) |
            Q(accessoryType__icontains=search) |
            Q(description__icontains=search)
        )
    if type_filter:
        accessories = accessories.filter(accessoryType__iexact=type_filter)

    accessories = accessories.order_by('accessoryType', 'accessoryName')

    all_types = Accessory.objects.values_list(
        'accessoryType', flat=True).distinct().order_by('accessoryType')

    return render(request, 'compare/admin/accessory_list.html', {
        'accessories':  accessories,
        'total':        Accessory.objects.count(),
        'search':       search,
        'sel_type':     type_filter,
        'all_types':    all_types,
    })


@role_required(allowed_roles=['admin'])
def accessory_create(request):
    form = AccessoryForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('accessory_list')
    return render(request, 'compare/admin/accessory_form.html', {
        'form': form, 'action': 'Add'
    })


@role_required(allowed_roles=['admin'])
def accessory_update(request, pk):
    accessory = get_object_or_404(Accessory, pk=pk)
    form = AccessoryForm(request.POST or None, instance=accessory)
    if form.is_valid():
        form.save()
        return redirect('accessory_list')
    return render(request, 'compare/admin/accessory_form.html', {
        'form': form, 'action': 'Edit', 'accessory': accessory
    })


@role_required(allowed_roles=['admin'])
def accessory_delete(request, pk):
    accessory = get_object_or_404(Accessory, pk=pk)
    accessory.delete()
    return redirect('accessory_list')


# ============================================================
#  CAR VARIANT MANAGEMENT (Admin)
# ============================================================

@role_required(allowed_roles=['admin'])
def variant_list(request, car_pk):
    car = get_object_or_404(Car, pk=car_pk)
    variants = CarVariant.objects.filter(car=car).order_by('price')
    return render(request, 'compare/admin/variant_list.html', {
        'car': car, 'variants': variants
    })


@role_required(allowed_roles=['admin'])
def variant_create(request, car_pk):
    car = get_object_or_404(Car, pk=car_pk)
    form = CarVariantForm(request.POST or None)
    if form.is_valid():
        variant = form.save(commit=False)
        variant.car = car
        variant.save()
        return redirect('variant_list', car_pk=car.pk)
    return render(request, 'compare/admin/variant_form.html', {
        'form': form, 'car': car, 'action': 'Add'
    })


@role_required(allowed_roles=['admin'])
def variant_update(request, car_pk, pk):
    car     = get_object_or_404(Car, pk=car_pk)
    variant = get_object_or_404(CarVariant, pk=pk, car=car)
    form    = CarVariantForm(request.POST or None, instance=variant)
    if form.is_valid():
        form.save()
        return redirect('variant_list', car_pk=car.pk)
    return render(request, 'compare/admin/variant_form.html', {
        'form': form, 'car': car, 'action': 'Edit', 'variant': variant
    })


@role_required(allowed_roles=['admin'])
def variant_delete(request, car_pk, pk):
    variant = get_object_or_404(CarVariant, pk=pk, car_id=car_pk)
    variant.delete()
    return redirect('variant_list', car_pk=car_pk)


# ============================================================
#  EXPORT CSV VIEWS (Admin)
# ============================================================
import csv
from django.http import HttpResponse


@role_required(allowed_roles=['admin'])
def export_cars_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="vehiclevault_cars.csv"'

    writer = csv.writer(response)
    writer.writerow([
        'ID', 'Car Name', 'Brand', 'Price (₹)', 'Fuel Type',
        'Transmission', 'Mileage (km/l)', 'Launch Year', 'Status'
    ])

    for car in Car.objects.all().order_by('id'):
        writer.writerow([
            car.id, car.carName, car.brand, car.price,
            car.fuelType, car.transmission, car.mileage,
            car.launchYear, 'Active' if car.status else 'Inactive'
        ])

    return response


@role_required(allowed_roles=['admin'])
def export_users_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="vehiclevault_users.csv"'

    writer = csv.writer(response)
    writer.writerow([
        'ID', 'First Name', 'Last Name', 'Email',
        'Gender', 'Role', 'Status', 'Joined On'
    ])

    for user in User.objects.all().order_by('id'):
        writer.writerow([
            user.id, user.first_name or '', user.last_name or '',
            user.email, user.gender or '', user.role,
            'Active' if user.is_active else 'Inactive',
            user.created_at.strftime('%d-%m-%Y') if user.created_at else ''
        ])

    return response


@role_required(allowed_roles=['admin'])
def export_reviews_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="vehiclevault_reviews.csv"'

    writer = csv.writer(response)
    writer.writerow([
        'ID', 'Car', 'Brand', 'User Email',
        'Rating', 'Comment', 'Date'
    ])

    for review in Review.objects.select_related('car', 'user').order_by('-createdAt'):
        writer.writerow([
            review.id, review.car.carName, review.car.brand,
            review.user.email, review.rating,
            review.comment, review.createdAt.strftime('%d-%m-%Y')
        ])

    return response


@role_required(allowed_roles=['admin'])
def export_comparisons_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="vehiclevault_comparisons.csv"'

    writer = csv.writer(response)
    writer.writerow([
        'ID', 'User Email', 'Car 1', 'Car 2', 'Compared On'
    ])

    comps = list(Comparison.objects.select_related('user', 'car1', 'car2').order_by('comparedAt'))
    for i, comp in enumerate(comps, 1):
        writer.writerow([
            i, comp.user.email,
            comp.car1.carName, comp.car2.carName,
            comp.comparedAt.strftime('%d-%m-%Y %H:%M')
        ])

    return response


# ============================================================
#  EXPORT PDF VIEWS (Admin)
# ============================================================
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT

RED   = colors.HexColor('#e63946')
DARK  = colors.HexColor('#0f172a')
TEAL  = colors.HexColor('#0d9488')
LIGHT = colors.HexColor('#f8fafc')
MUTED = colors.HexColor('#334155')  # dark slate — readable on white
WHITE = colors.white


def _pdf_base_style():
    """Return common TableStyle elements."""
    return [
        ('BACKGROUND',   (0, 0), (-1, 0), DARK),
        ('TEXTCOLOR',    (0, 0), (-1, 0), WHITE),
        ('FONTNAME',     (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE',     (0, 0), (-1, 0), 9),
        ('ALIGN',        (0, 0), (-1, 0), 'CENTER'),
        ('BOTTOMPADDING',(0, 0), (-1, 0), 8),
        ('TOPPADDING',   (0, 0), (-1, 0), 8),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [WHITE, LIGHT]),
        ('FONTNAME',     (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE',     (0, 1), (-1, -1), 8),
        ('ALIGN',        (0, 1), (-1, -1), 'LEFT'),
        ('TOPPADDING',   (0, 1), (-1, -1), 6),
        ('BOTTOMPADDING',(0, 1), (-1, -1), 6),
        ('LEFTPADDING',  (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ('GRID',         (0, 0), (-1, -1), 0.4, colors.HexColor('#e2e8f0')),
        ('BOX',          (0, 0), (-1, -1), 1,   DARK),
    ]


def _register_unicode_fonts():
    """Register a Unicode font that supports Rs. symbol — works on Windows, Linux & Mac."""
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    import os, sys

    # Already registered — skip
    if 'DVSans' in pdfmetrics.getRegisteredFontNames():
        return 'DVSans', 'DVSans-Bold'

    # Font search paths for Windows / Linux / Mac
    candidates = []

    if sys.platform == 'win32':
        win = os.environ.get('WINDIR', 'C:\\Windows')
        candidates += [
            (os.path.join(win, 'Fonts', 'arial.ttf'),
             os.path.join(win, 'Fonts', 'arialbd.ttf')),
            (os.path.join(win, 'Fonts', 'calibri.ttf'),
             os.path.join(win, 'Fonts', 'calibrib.ttf')),
            (os.path.join(win, 'Fonts', 'verdana.ttf'),
             os.path.join(win, 'Fonts', 'verdanab.ttf')),
            (os.path.join(win, 'Fonts', 'tahoma.ttf'),
             os.path.join(win, 'Fonts', 'tahomabd.ttf')),
        ]
    else:
        # Linux
        candidates += [
            ('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
             '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'),
            ('/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf',
             '/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf'),
        ]
        # Mac
        candidates += [
            ('/Library/Fonts/Arial.ttf',       '/Library/Fonts/Arial Bold.ttf'),
            ('/System/Library/Fonts/Helvetica.ttc', '/System/Library/Fonts/Helvetica.ttc'),
        ]

    for reg_path, bold_path in candidates:
        if os.path.exists(reg_path):
            try:
                pdfmetrics.registerFont(TTFont('DVSans',      reg_path))
                pdfmetrics.registerFont(TTFont('DVSans-Bold',
                    bold_path if os.path.exists(bold_path) else reg_path))
                return 'DVSans', 'DVSans-Bold'
            except Exception:
                continue

    # Final fallback — Helvetica (no Rs. but won't crash)
    return 'Helvetica', 'Helvetica-Bold'


def _build_pdf(response, title, subtitle, headers, rows, col_widths=None):
    """Build a branded PDF and write it to response."""
    from reportlab.platypus import HRFlowable
    import uuid

    font_reg, font_bold = _register_unicode_fonts()

    doc = SimpleDocTemplate(
        response,
        pagesize=landscape(A4),
        leftMargin=18*mm, rightMargin=18*mm,
        topMargin=16*mm,  bottomMargin=16*mm,
    )
    story = []

    # Use unique style names each call to avoid ReportLab style cache conflicts
    uid = uuid.uuid4().hex[:8]

    # Title — large, dark, bold
    story.append(Paragraph(f'VehicleVault — {title}',
        ParagraphStyle(f'vv_title_{uid}',
            fontName=font_bold,
            fontSize=20,
            textColor=colors.HexColor('#0f172a'),
            spaceAfter=4,
            leading=24,
        )))

    # Subtitle — medium, clearly readable dark grey
    story.append(Paragraph(subtitle,
        ParagraphStyle(f'vv_sub_{uid}',
            fontName=font_reg,
            fontSize=11,
            textColor=colors.HexColor('#1e293b'),
            spaceAfter=8,
            leading=16,
        )))

    story.append(HRFlowable(width='100%', thickness=2.5, color=RED, spaceAfter=12))

    # Table — replace Rs symbol so it renders correctly
    def clean(val):
        if isinstance(val, str):
            return val.replace('₹', 'Rs.')
        return val

    table_data = [[clean(h) for h in headers]] + [[clean(v) for v in row] for row in rows]
    page_w = landscape(A4)[0] - 36*mm
    if col_widths is None:
        col_widths = [page_w / len(headers)] * len(headers)

    tbl = Table(table_data, colWidths=col_widths, repeatRows=1)
    style = _pdf_base_style()
    # Override fonts to Unicode-capable ones
    style += [
        ('FONTNAME', (0, 0), (-1,  0), font_bold),
        ('FONTNAME', (0, 1), (0,  -1), font_bold),
        ('FONTNAME', (1, 1), (-1, -1), font_reg),
    ]
    tbl.setStyle(TableStyle(style))
    story.append(tbl)

    story.append(Spacer(1, 10))
    story.append(Paragraph(
        f'Generated by VehicleVault Admin Panel  ·  Total records: {len(rows)}',
        ParagraphStyle(f'vv_foot_{uid}',
            fontName=font_reg,
            fontSize=8,
            textColor=colors.HexColor('#475569'),
            alignment=TA_CENTER,
        )
    ))

    doc.build(story)


@role_required(allowed_roles=['admin'])
def export_cars_pdf(request):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="vehiclevault_cars.pdf"'

    from datetime import date
    headers = ['#', 'Car Name', 'Brand', 'Price (₹)', 'Fuel', 'Transmission', 'Mileage', 'Year', 'Status']
    rows = []
    for i, car in enumerate(Car.objects.all().order_by('id'), 1):
        rows.append([
            str(i), car.carName, car.brand,
            f'Rs.{car.price:,}', car.fuelType, car.transmission,
            f'{car.mileage} km/l', str(car.launchYear),
            'Active' if car.status else 'Inactive',
        ])

    page_w = landscape(A4)[0] - 36*mm
    col_widths = [12*mm, 45*mm, 35*mm, 28*mm, 24*mm, 30*mm, 24*mm, 18*mm, 22*mm]

    _build_pdf(
        response,
        title='Cars Report',
        subtitle=f'Complete car catalogue  ·  Exported on {date.today().strftime("%d %B %Y")}',
        headers=headers,
        rows=rows,
        col_widths=col_widths,
    )
    return response


@role_required(allowed_roles=['admin'])
def export_users_pdf(request):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="vehiclevault_users.pdf"'

    from datetime import date
    headers = ['#', 'First Name', 'Last Name', 'Email', 'Gender', 'Role', 'Status', 'Joined']
    rows = []
    for i, user in enumerate(User.objects.all().order_by('id'), 1):
        rows.append([
            str(i),
            user.first_name or '—', user.last_name or '—',
            user.email, user.gender or '—', user.role,
            'Active' if user.is_active else 'Inactive',
            user.created_at.strftime('%d-%m-%Y') if user.created_at else '—',
        ])

    col_widths = [12*mm, 28*mm, 28*mm, 60*mm, 20*mm, 18*mm, 20*mm, 28*mm]
    _build_pdf(
        response,
        title='Users Report',
        subtitle=f'All registered users  ·  Exported on {date.today().strftime("%d %B %Y")}',
        headers=headers, rows=rows, col_widths=col_widths,
    )
    return response


@role_required(allowed_roles=['admin'])
def export_reviews_pdf(request):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="vehiclevault_reviews.pdf"'

    from datetime import date
    headers = ['#', 'Car', 'Brand', 'User Email', 'Rating', 'Comment', 'Date']
    rows = []
    for i, r in enumerate(Review.objects.select_related('car', 'user').order_by('createdAt'), 1):
        comment = r.comment[:60] + '...' if len(r.comment) > 60 else r.comment
        rows.append([
            str(i), r.car.carName, r.car.brand,
            r.user.email, f'{r.rating}/5', comment,
            r.createdAt.strftime('%d-%m-%Y'),
        ])

    col_widths = [12*mm, 38*mm, 28*mm, 55*mm, 18*mm, 72*mm, 28*mm]
    _build_pdf(
        response,
        title='Reviews Report',
        subtitle=f'All customer reviews  ·  Exported on {date.today().strftime("%d %B %Y")}',
        headers=headers, rows=rows, col_widths=col_widths,
    )
    return response


@role_required(allowed_roles=['admin'])
def export_comparisons_pdf(request):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="vehiclevault_comparisons.pdf"'

    from datetime import date
    headers = ['#', 'User Email', 'Car 1', 'Car 2', 'Compared On']
    rows = []
    comps = list(Comparison.objects.select_related('user', 'car1', 'car2').order_by('comparedAt'))
    for i, c in enumerate(comps, 1):
        rows.append([
            str(i), c.user.email,
            c.car1.carName, c.car2.carName,
            c.comparedAt.strftime('%d-%m-%Y %H:%M'),
        ])

    col_widths = [12*mm, 70*mm, 55*mm, 55*mm, 40*mm]
    _build_pdf(
        response,
        title='Comparisons Report',
        subtitle=f'All car comparisons  ·  Exported on {date.today().strftime("%d %B %Y")}',
        headers=headers, rows=rows, col_widths=col_widths,
    )
    return response


# ============================================================
#  USER COMPARISON EXPORT (CSV + PDF)
# ============================================================
from django.contrib.auth.decorators import login_required

@login_required
def export_comparison_csv_user(request):
    """Export the current comparison (car IDs from GET params) as CSV."""
    car_ids = request.GET.getlist('cars')
    cars_qs = Car.objects.filter(id__in=car_ids)

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="my_comparison.csv"'

    writer = csv.writer(response)
    writer.writerow(['Specification'] + [c.carName for c in cars_qs])
    writer.writerow(['Brand']        + [c.brand for c in cars_qs])
    writer.writerow(['Price (₹)']    + [f'₹{c.price:,}' for c in cars_qs])
    writer.writerow(['Fuel Type']    + [c.fuelType for c in cars_qs])
    writer.writerow(['Transmission'] + [c.transmission for c in cars_qs])
    writer.writerow(['Mileage (km/l)'] + [f'{c.mileage} km/l' for c in cars_qs])
    writer.writerow(['Launch Year']  + [str(c.launchYear) for c in cars_qs])

    from django.db.models import Avg
    for car in cars_qs:
        avg = Review.objects.filter(car=car).aggregate(Avg('rating'))['rating__avg'] or 0
        writer.writerow([f'Avg Rating ({car.carName})'] + [f'{round(avg,1)}/5'])

    return response


@login_required
def export_comparison_pdf_user(request):
    """Export the current comparison (car IDs from GET params) as a branded PDF."""
    from django.db.models import Avg
    from datetime import date
    from reportlab.lib.pagesizes import A4, landscape
    from reportlab.lib import colors as rl_colors
    from reportlab.lib.units import mm
    from reportlab.platypus import (
        SimpleDocTemplate, Table, TableStyle,
        Paragraph, Spacer, HRFlowable
    )
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.lib.enums import TA_CENTER, TA_LEFT
    # ── Register Unicode fonts (cross-platform: Windows/Linux/Mac) ──
    font_reg, font_bold = _register_unicode_fonts()

    # ── Colours ────────────────────────────────────────────────────
    C_RED   = rl_colors.HexColor('#e63946')
    C_DARK  = rl_colors.HexColor('#0f172a')
    C_DARK2 = rl_colors.HexColor('#1e293b')
    C_LIGHT = rl_colors.HexColor('#f8fafc')
    C_ALT   = rl_colors.HexColor('#f1f5f9')
    C_MUTED = rl_colors.HexColor('#334155')  # dark slate — readable on white
    C_ORANGE= rl_colors.HexColor('#f4a261')
    C_TEAL  = rl_colors.HexColor('#0d9488')
    C_GRID  = rl_colors.HexColor('#e2e8f0')

    car_ids  = request.GET.getlist('cars')
    cars_qs  = list(Car.objects.filter(id__in=car_ids))

    response = HttpResponse(content_type='application/pdf')
    names    = ' vs '.join(c.carName for c in cars_qs)
    response['Content-Disposition'] = f'attachment; filename="VehicleVault_{names}.pdf"'

    PAGE   = landscape(A4)
    L_MAR  = 18*mm
    doc    = SimpleDocTemplate(
        response, pagesize=PAGE,
        leftMargin=L_MAR, rightMargin=L_MAR,
        topMargin=14*mm,  bottomMargin=14*mm,
    )

    # ── Styles — unique names to avoid ReportLab global style cache ──
    import uuid as _uuid
    _uid = _uuid.uuid4().hex[:8]

    def S(name, **kw):
        return ParagraphStyle(f'{name}_{_uid}', **kw)

    sTitle = S('title', fontName=font_bold, fontSize=22,
               textColor=C_DARK, spaceAfter=4, leading=26)
    sSub   = S('sub',   fontName=font_reg,  fontSize=11,
               textColor=rl_colors.HexColor('#1e293b'), spaceAfter=4, leading=16)
    sFoot  = S('foot',  fontName=font_reg,  fontSize=8,
               textColor=rl_colors.HexColor('#475569'), alignment=TA_CENTER)

    story = []

    # ── Header block ───────────────────────────────────────────────
    story.append(Paragraph('VehicleVault', sTitle))
    story.append(Paragraph(
        f'Car Comparison Report  ·  {request.user.email}  ·  {date.today().strftime("%d %B %Y")}',
        sSub
    ))
    story.append(Spacer(1, 6))
    story.append(HRFlowable(width='100%', thickness=2.5, color=C_RED,
                            spaceAfter=0, spaceBefore=0))
    story.append(HRFlowable(width='100%', thickness=0.5, color=C_GRID,
                            spaceAfter=14, spaceBefore=2))

    # ── Data rows ──────────────────────────────────────────────────
    specs = [
        ('Car Name',      [c.carName                              for c in cars_qs]),
        ('Brand',         [c.brand                                for c in cars_qs]),
        ('Price',         [f'Rs. {c.price:,}'                     for c in cars_qs]),
        ('Fuel Type',     [c.fuelType                             for c in cars_qs]),
        ('Transmission',  [c.transmission                         for c in cars_qs]),
        ('Mileage',       [f'{c.mileage} km/l'                    for c in cars_qs]),
        ('Launch Year',   [str(c.launchYear)                      for c in cars_qs]),
        ('Avg Rating',    [
            f"{round(Review.objects.filter(car=c).aggregate(Avg('rating'))['rating__avg'] or 0, 1)} / 5"
            for c in cars_qs
        ]),
    ]

    # Header row: "Specification" + car names
    header_row = [
        Paragraph('Specification', S('h', fontName=font_bold, fontSize=9,
                                     textColor=rl_colors.white, alignment=TA_LEFT))
    ] + [
        Paragraph(c.carName, S('hn', fontName=font_bold, fontSize=10,
                               textColor=rl_colors.white, alignment=TA_CENTER))
        for c in cars_qs
    ]

    # Spec rows
    table_rows = [header_row]
    for i, (label, values) in enumerate(specs):
        is_price = (label == 'Price')
        row_bg   = C_LIGHT if i % 2 == 0 else rl_colors.white

        row = [
            Paragraph(label, S(f'lbl{i}', fontName=font_bold, fontSize=9,
                               textColor=C_DARK2, alignment=TA_LEFT))
        ]
        for v in values:
            para = Paragraph(
                v,
                S(f'val{i}', fontName=font_bold if is_price else font_reg,
                  fontSize=9,
                  textColor=C_ORANGE if is_price else C_DARK,
                  alignment=TA_CENTER)
            )
            row.append(para)
        table_rows.append(row)

    # ── Column widths ──────────────────────────────────────────────
    page_w  = PAGE[0] - 2 * L_MAR
    spec_w  = 50*mm
    n_cars  = len(cars_qs)
    car_w   = (page_w - spec_w) / max(n_cars, 1)
    col_w   = [spec_w] + [car_w] * n_cars

    tbl = Table(table_rows, colWidths=col_w, repeatRows=1)
    tbl.setStyle(TableStyle([
        # Header row
        ('BACKGROUND',    (0, 0), (-1, 0), C_DARK),
        ('TOPPADDING',    (0, 0), (-1, 0), 11),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 11),
        ('LEFTPADDING',   (0, 0), (-1, 0), 12),
        ('RIGHTPADDING',  (0, 0), (-1, 0), 12),
        # Data rows padding
        ('TOPPADDING',    (0, 1), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 10),
        ('LEFTPADDING',   (0, 1), (-1, -1), 12),
        ('RIGHTPADDING',  (0, 1), (-1, -1), 12),
        # Alternating row backgrounds
        *[('BACKGROUND', (0, i), (-1, i), C_LIGHT if i % 2 == 0 else rl_colors.white)
          for i in range(1, len(table_rows))],
        # Spec label column tint
        *[('BACKGROUND', (0, i), (0, i), C_ALT)
          for i in range(1, len(table_rows))],
        # Left border accent on spec column
        ('LINEAFTER',     (0, 0), (0, -1), 2, C_RED),
        # Grid lines
        ('INNERGRID',     (0, 0), (-1, -1), 0.4, C_GRID),
        ('BOX',           (0, 0), (-1, -1), 1.5, C_DARK),
        # Bottom line under header
        ('LINEBELOW',     (0, 0), (-1, 0), 1.5, C_RED),
        # Valign
        ('VALIGN',        (0, 0), (-1, -1), 'MIDDLE'),
    ]))

    story.append(tbl)
    story.append(Spacer(1, 14))

    # ── Footer ─────────────────────────────────────────────────────
    story.append(HRFlowable(width='100%', thickness=0.5, color=C_GRID,
                            spaceAfter=6, spaceBefore=0))
    story.append(Paragraph(
        f'Downloaded from VehicleVault  ·  Generated on {date.today().strftime("%d %B %Y")}  ·  vehiclevault.com',
        sFoot
    ))

    doc.build(story)
    return response


# ============================================================
#  WISHLIST VIEWS
# ============================================================

@login_required
def toggle_wishlist(request, car_id):
    """Add or remove a car from the user's wishlist (AJAX-friendly)."""
    car  = Car.objects.get(id=car_id)
    obj, created = Wishlist.objects.get_or_create(user=request.user, car=car)

    if not created:
        obj.delete()   # already in wishlist → remove
        saved = False
    else:
        saved = True   # just added

    # AJAX response
    from django.http import JsonResponse
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'saved': saved, 'count': Wishlist.objects.filter(user=request.user).count()})

    # Normal redirect back
    return redirect(request.META.get('HTTP_REFERER', 'public_car_list'))


@login_required
def user_wishlist(request):
    """Show all wishlisted cars for the logged-in user."""
    items = Wishlist.objects.filter(
        user=request.user
    ).select_related('car').order_by('-savedAt')

    return render(request, 'compare/user/user_wishlist.html', {
        'wishlist_items': items,
    })
