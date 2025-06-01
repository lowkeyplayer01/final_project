from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator

class Feedback(models.Model):
    created_date = models.DateTimeField(auto_now_add=True)
    suggestions  = models.TextField()
    user         = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"Feedback by {self.user.username}"


class Category(models.Model):
    title = models.CharField(max_length=255)

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ["title"]

    def __str__(self):
        return self.title




class Dish(models.Model):
    name        = models.CharField(max_length=50)
    description = models.TextField(blank=True)
    categories  = models.ManyToManyField(Category, blank=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name

class Restaurant(models.Model):
    name          = models.CharField(max_length=50)
    description   = models.TextField(blank=True)
    address       = models.TextField()
    contact_phone = models.CharField(max_length=20)
    website       = models.URLField(blank=True)

    def __str__(self):
        return self.name


class DishRestaurant(models.Model):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.PROTECT)
    dish       = models.ForeignKey(Dish,       on_delete=models.PROTECT)
    local_name = models.CharField(max_length=100,blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["restaurant","dish"],
                name="combo_dish_res"
            ),
        ]

    def __str__(self):
        name = self.local_name or self.dish.name
        return f"{self.restaurant.name} – {name}"




class Review(models.Model):
    created_date    = models.DateTimeField(auto_now_add=True)
    rating          = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(5.0)]
    )
    price_paid      = models.IntegerField()
    description     = models.TextField()
    photo           = models.ImageField(upload_to='reviews/', blank=True, null=True)
    user            = models.ForeignKey(User, on_delete=models.CASCADE)
    dish_restaurant = models.ForeignKey(
        DishRestaurant, on_delete=models.CASCADE, related_name='reviews'
    )

    def __str__(self):
        return f"{self.user.username}'s review of {self.dish_restaurant}"

class Wishlist(models.Model):
    created_date = models.DateTimeField(auto_now_add=True)
    comments     = models.TextField(blank=True)
    user         = models.ForeignKey(User, on_delete=models.CASCADE)
    dish         = models.ForeignKey(Dish, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('user', 'dish')

    def __str__(self):
        return f"{self.user.username} wants {self.dish.name}"
    


class Review(models.Model):
    created_date    = models.DateTimeField(auto_now_add=True)
    rating          = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(5.0)]
    )
    price_paid      = models.IntegerField()
    description     = models.TextField()
    photo           = models.ImageField(upload_to='reviews/', blank=True, null=True)
    user            = models.ForeignKey(User, on_delete=models.CASCADE)
    dish_restaurant = models.ForeignKey(
        DishRestaurant, on_delete=models.CASCADE, related_name='reviews'
    )

    def __str__(self):
        return f"{self.user.username}'s review of {self.dish_restaurant}"

    def clean(self):
        from django.core.exceptions import ValidationError

        if self.rating is not None and self.price_paid is not None:
            if self.rating < 1.0 and self.price_paid <= 0:
                raise ValidationError(
                    {"price_paid": "If rating < 1.0, price_paid must be > 0."}
                )

