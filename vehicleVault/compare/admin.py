from django.contrib import admin
from .models import (
    Car, CarVariant, Accessory, CarAccessoryMapping,
    Comparison, Review, UserPreference, SearchHistory, UserInteraction, CarPriceHistory
)
# Register your models here.

 # ── Car ──────────────────────────────────────────────────────────
class CarVariantInline(admin.TabularInline):
    model = CarVariant
    extra = 1
    fields = ['variantName', 'variantTier', 'price', 'mileage', 'transmission', 'isAvailable']
 
 
@admin.register(Car)
class CarAdmin(admin.ModelAdmin):
    list_display  = ['carName', 'brand', 'price', 'fuelType', 'transmission', 'mileage', 'launchYear', 'status']
    list_filter   = ['brand', 'fuelType', 'transmission', 'status', 'launchYear']
    search_fields = ['carName', 'brand']
    list_editable = ['status']
    ordering      = ['brand', 'carName']
    inlines       = [CarVariantInline]
    fieldsets = (
        ('Basic Info',   {'fields': ('carName', 'brand', 'launchYear', 'status')}),
        ('Specs',        {'fields': ('price', 'fuelType', 'transmission', 'mileage')}),
        ('Media',        {'fields': ('carImage', 'model_3d')}),
    )
 
 
# ── Car Variant ───────────────────────────────────────────────────
@admin.register(CarVariant)
class CarVariantAdmin(admin.ModelAdmin):
    list_display  = ['variantName', 'car', 'variantTier', 'price', 'mileage', 'transmission', 'isAvailable']
    list_filter   = ['variantTier', 'isAvailable', 'car__brand']
    search_fields = ['variantName', 'car__carName']
    list_editable = ['isAvailable']
    ordering      = ['car', 'price']
 
 
# ── Accessory ─────────────────────────────────────────────────────
@admin.register(Accessory)
class AccessoryAdmin(admin.ModelAdmin):
    list_display  = ['accessoryName', 'accessoryType', 'price']
    list_filter   = ['accessoryType']
    search_fields = ['accessoryName', 'accessoryType']
    ordering      = ['accessoryType', 'accessoryName']
 
 
# ── Car Accessory Mapping ─────────────────────────────────────────
@admin.register(CarAccessoryMapping)
class CarAccessoryMappingAdmin(admin.ModelAdmin):
    list_display  = ['car', 'accessory']
    search_fields = ['car__carName', 'accessory__accessoryName']
    autocomplete_fields = ['car', 'accessory']
 
 
# ── Review ────────────────────────────────────────────────────────
@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display  = ['car', 'user', 'rating', 'createdAt']
    list_filter   = ['rating', 'car__brand']
    search_fields = ['car__carName', 'user__email', 'comment']
    readonly_fields = ['createdAt']
    ordering      = ['-createdAt']
 
 
# ── Comparison ────────────────────────────────────────────────────
@admin.register(Comparison)
class ComparisonAdmin(admin.ModelAdmin):
    list_display  = ['user', 'car1', 'car2', 'comparedAt']
    list_filter   = ['car1__brand', 'car2__brand']
    search_fields = ['user__email', 'car1__carName', 'car2__carName']
    readonly_fields = ['comparedAt']
    ordering      = ['-comparedAt']
 
 
# ── User Preference ───────────────────────────────────────────────
@admin.register(UserPreference)
class UserPreferenceAdmin(admin.ModelAdmin):
    list_display  = ['user', 'preferredFuel', 'maxBudget', 'preferredBrand']
    search_fields = ['user__email', 'preferredBrand']
 
 
# ── Search History ────────────────────────────────────────────────
@admin.register(SearchHistory)
class SearchHistoryAdmin(admin.ModelAdmin):
    list_display  = ['user', 'keyword', 'searchedAt']
    search_fields = ['user__email', 'keyword']
    readonly_fields = ['searchedAt']
    ordering      = ['-searchedAt']
 
 
# ── Car Price History ────────────────────────────────────────────
class CarPriceHistoryInline(admin.TabularInline):
    model = CarPriceHistory
    extra = 1
    fields = ['recorded_on', 'price', 'note']
    ordering = ['recorded_on']
 
 
@admin.register(CarPriceHistory)
class CarPriceHistoryAdmin(admin.ModelAdmin):
    list_display  = ['car', 'price', 'recorded_on', 'note']
    list_filter   = ['car__brand', 'recorded_on']
    search_fields = ['car__carName', 'note']
    ordering      = ['-recorded_on']
    date_hierarchy = 'recorded_on'


# ── User Interaction ──────────────────────────────────────────────
@admin.register(UserInteraction)
class UserInteractionAdmin(admin.ModelAdmin):
    list_display  = ['user', 'car', 'interactionType', 'interactionDate', 'deviceType']
    list_filter   = ['interactionType', 'deviceType']
    search_fields = ['user__email', 'car__carName']
    ordering      = ['-interactionDate']
 