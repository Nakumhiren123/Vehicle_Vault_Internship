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

    class Meta:
        db_table = "car"

    def __str__(self):
        return self.carName



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