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


# ── Car Battle / Voting ───────────────────────────────────────────
class CarBattle(models.Model):
    """A head-to-head battle between two cars where users vote."""
    car1        = models.ForeignKey(Car, on_delete=models.CASCADE, related_name='battles_as_car1')
    car2        = models.ForeignKey(Car, on_delete=models.CASCADE, related_name='battles_as_car2')
    title       = models.CharField(max_length=200, blank=True)
    votes_car1  = models.PositiveIntegerField(default=0)
    votes_car2  = models.PositiveIntegerField(default=0)
    is_active   = models.BooleanField(default=True)
    createdAt   = models.DateTimeField(auto_now_add=True)
 
    class Meta:
        db_table = "car_battle"
 
    def __str__(self):
        return f"{self.car1.carName} vs {self.car2.carName}"
 
    def total_votes(self):
        return self.votes_car1 + self.votes_car2
 
    def pct1(self):
        total = self.total_votes()
        return round((self.votes_car1 / total) * 100) if total > 0 else 50
 
    def pct2(self):
        total = self.total_votes()
        return round((self.votes_car2 / total) * 100) if total > 0 else 50
 
 
class BattleVote(models.Model):
    """Tracks which user voted in which battle (prevents double voting)."""
    battle  = models.ForeignKey(CarBattle, on_delete=models.CASCADE, related_name='vote_records')
    user    = models.ForeignKey('core.User', on_delete=models.CASCADE)
    voted_for = models.IntegerField(choices=[(1, 'Car 1'), (2, 'Car 2')])
    votedAt = models.DateTimeField(auto_now_add=True)
 
    class Meta:
        db_table = "battle_vote"
        unique_together = ('battle', 'user')  # one vote per battle per user
 
    def __str__(self):
        return f"{self.user.email} voted in battle {self.battle.id}"
    

# ── Car Price History ─────────────────────────────────────────────
class CarPriceHistory(models.Model):
    """Records price changes for a car over time."""
    car       = models.ForeignKey(Car, on_delete=models.CASCADE, related_name='price_history')
    price     = models.IntegerField()
    note      = models.CharField(max_length=200, blank=True,
                    help_text="e.g. 'Price hike', 'Festive discount', 'New variant launch'")
    recorded_on = models.DateField()
    createdAt   = models.DateTimeField(auto_now_add=True)
 
    class Meta:
        db_table  = 'car_price_history'
        ordering  = ['recorded_on']
 
    def __str__(self):
        return f"{self.car.carName} — ₹{self.price} on {self.recorded_on}"
    

# ── Car Ownership History ─────────────────────────────────────────

class CarOwnership(models.Model):
   
    car            = models.ForeignKey(Car, on_delete=models.CASCADE,
                                       related_name='ownership_history')
    owner_name     = models.CharField(max_length=150,
                                      help_text='Full name of the owner')
    owner_contact  = models.CharField(max_length=100, blank=True,
                                      help_text='Phone / email (admin-only, not shown to users)')
    purchase_date  = models.DateField(help_text='Date this owner purchased / received the car')
    sale_date      = models.DateField(null=True, blank=True,
                                      help_text='Date this owner sold the car (leave blank if still current owner)')
    purchase_price = models.IntegerField(null=True, blank=True,
                                         help_text='Price at which this owner bought the car (₹)')
    notes          = models.TextField(blank=True,
                                      help_text='e.g. accident history, condition at handover')
    createdAt      = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'car_ownership'
        ordering = ['purchase_date']

    def __str__(self):
        status = 'current' if not self.sale_date else f'sold {self.sale_date}'
        return f"{self.car.carName} — {self.owner_name} ({status})"

    @property
    def is_current_owner(self):
        return self.sale_date is None

    @property
    def duration_days(self):
        """How many days this person owned / has owned the car."""
        from datetime import date
        end = self.sale_date or date.today()
        return (end - self.purchase_date).days

    @property
    def duration_display(self):
        days = self.duration_days
        years  = days // 365
        months = (days % 365) // 30
        parts = []
        if years:
            parts.append(f"{years} yr{'s' if years > 1 else ''}")
        if months:
            parts.append(f"{months} mo")
        if not parts:
            parts.append(f"{days} day{'s' if days != 1 else ''}")
        return ' '.join(parts)
    