from django.db import models

# Create your models here.

# 1️ User Table

# class User(models.Model):
#     userFirstName = models.CharField(max_length=100)
#     userLastName = models.CharField(max_length=100)
#     userEmail = models.EmailField(unique=True)
#     userPassword = models.CharField(max_length=255)
#     userPhone = models.CharField(max_length=15, null=True)
#     userCreatedAt = models.DateTimeField(auto_now_add=True)
#     userStatus = models.BooleanField(default=True)

#     class Meta:
#         db_table = "user"

#     def __str__(self):
#         return self.userName



# # 2️ Admin Table (OneToOne with User)

# class Admin(models.Model):
#     user = models.OneToOneField(User, on_delete=models.CASCADE)
#     adminRole = models.CharField(max_length=50)
#     adminAccessLevel = models.IntegerField()

#     class Meta:
#         db_table = "admin"

#     def __str__(self):
#         return f"Admin - {self.user.userName}"



# 3️ Car Table

class Car(models.Model):
    carName = models.CharField(max_length=100)
    brand = models.CharField(max_length=100)
    price = models.IntegerField()
    fuelType = models.CharField(max_length=30)
    transmission = models.CharField(max_length=30)
    mileage = models.FloatField()
    launchYear = models.IntegerField()
    status = models.BooleanField(default=True)
    carImage = models.ImageField(upload_to='cars/', null=True, blank=True)
    # models.py
    model_3d = models.FileField(upload_to='car_models/', null=True, blank=True)
    car3DModel = models.FileField(upload_to='car_models/', blank=True, null=True)
    sketchfabId = models.CharField(max_length=64, blank=True, null=True)

    class Meta:
        db_table = "car"

    def __str__(self):
        return self.carName

class CarImage(models.Model):
    car     = models.ForeignKey(Car, on_delete=models.CASCADE, related_name='gallery_images')
    image   = models.ImageField(upload_to='cars/gallery/')
    caption = models.CharField(max_length=100, blank=True)
    order   = models.PositiveIntegerField(default=0)   # for sorting

    class Meta:
        db_table = "car_image"
        ordering = ['order', 'id']

    def __str__(self):
        return f"{self.car.carName} — image {self.id}"
    
VARIANT_CHOICES = [
    ('Base',    'Base'),
    ('Mid',     'Mid'),
    ('Top',     'Top'),
    ('Special', 'Special Edition'),
]
 
class CarVariant(models.Model):
    car          = models.ForeignKey(Car, on_delete=models.CASCADE, related_name='variants')
    variantName  = models.CharField(max_length=100)          # e.g. "LXi", "VXi", "ZXi+"
    variantTier  = models.CharField(max_length=20, choices=VARIANT_CHOICES, default='Base')
    price        = models.IntegerField()
    mileage      = models.FloatField(null=True, blank=True)  # variant-specific mileage
    transmission = models.CharField(max_length=30, blank=True)
    features     = models.TextField(blank=True,
                       help_text="Comma-separated list of features, e.g. Sunroof, Cruise Control")
    isAvailable  = models.BooleanField(default=True)
 
    class Meta:
        db_table = 'car_variant'
        ordering = ['price']
 
    def __str__(self):
        return f"{self.car.carName} — {self.variantName}"
 
    def features_list(self):
        return [f.strip() for f in self.features.split(',') if f.strip()]
    
# 4️ Accessory Table

class Accessory(models.Model):
    accessoryName = models.CharField(max_length=100)
    accessoryType = models.CharField(max_length=50)
    price = models.IntegerField()
    description = models.TextField()

    class Meta:
        db_table = "accessory"

    def __str__(self):
        return self.accessoryName



# 5️ Car_Accessory_Mapping (FK + FK)

class CarAccessoryMapping(models.Model):
    car = models.ForeignKey(Car, on_delete=models.CASCADE)
    accessory = models.ForeignKey(Accessory, on_delete=models.CASCADE)

    class Meta:
        db_table = "car_accessory_mapping"

    



# 6️ Comparison Table (FK User + FK Car)

class Comparison(models.Model):
    user = models.ForeignKey("core.User", on_delete=models.CASCADE)
    car1 = models.ForeignKey(Car, on_delete=models.CASCADE, related_name="car1")
    car2 = models.ForeignKey(Car, on_delete=models.CASCADE, related_name="car2")
    # car3 = models.ForeignKey(Car, on_delete=models.CASCADE, related_name="car3")
    # car4 = models.ForeignKey(Car, on_delete=models.CASCADE, related_name="car4")
    comparedAt = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "comparison"



# 7️ Review Table (FK User + FK Car)

class Review(models.Model):
    user = models.ForeignKey("core.User", on_delete=models.CASCADE)
    car = models.ForeignKey(Car, on_delete=models.CASCADE)
    rating = models.IntegerField()
    comment = models.TextField()
    createdAt = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "review"


# 8 User Preference (OneToOne User)

class UserPreference(models.Model):
    user = models.OneToOneField("core.User", on_delete=models.CASCADE)
    preferredFuel = models.CharField(max_length=30)
    maxBudget = models.IntegerField()
    preferredBrand = models.CharField(max_length=100)

    class Meta:
        db_table = "user_preference"



# 9️ Search History (FK User)

class SearchHistory(models.Model):
    user = models.ForeignKey("core.User", on_delete=models.CASCADE)
    keyword = models.CharField(max_length=200)
    searchedAt = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "search_history"



# 10 User Interaction (FK User + FK Car)

class UserInteraction(models.Model):
    user = models.ForeignKey("core.User", on_delete=models.CASCADE)
    car = models.ForeignKey(Car, on_delete=models.CASCADE)

    interactionType = models.CharField(max_length=30)
    durationSeconds = models.IntegerField(null=True)
    interactionDate = models.DateTimeField()
    deviceType = models.CharField(max_length=20, null=True)
    referrer = models.CharField(max_length=255, null=True)

    class Meta:
        db_table = "user_interaction"



# 11 Notification (FK User)

class Notification(models.Model):
    NOTIF_TYPES = [
        ('review',     'New Review'),
        ('comparison', 'Comparison Done'),
        ('welcome',    'Welcome'),
        ('car_added',  'New Car Added'),
        ('system',     'System Message'),
    ]
    user      = models.ForeignKey("core.User", on_delete=models.CASCADE, related_name='notifications')
    notifType = models.CharField(max_length=30, choices=NOTIF_TYPES, default='system')
    title     = models.CharField(max_length=150)
    message   = models.TextField()
    isRead    = models.BooleanField(default=False)
    link      = models.CharField(max_length=255, blank=True)   # optional URL to redirect to
    createdAt = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "notification"
        ordering = ['-createdAt']

    def __str__(self):
        return f"[{self.notifType}] {self.title} → {self.user.email}"

# 12 Wishlist / Saved Cars (FK User + FK Car)

class Wishlist(models.Model):
    user      = models.ForeignKey("core.User", on_delete=models.CASCADE, related_name='wishlist')
    car       = models.ForeignKey(Car, on_delete=models.CASCADE, related_name='wishlisted_by')
    savedAt   = models.DateTimeField(auto_now_add=True)
    note      = models.CharField(max_length=200, blank=True)   # optional personal note

    class Meta:
        db_table       = "wishlist"
        unique_together = [('user', 'car')]   # prevent duplicate saves
        ordering        = ['-savedAt']

    def __str__(self):
        return f"{self.user.email} saved {self.car.carName}"