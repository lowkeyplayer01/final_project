

# Register your models here.
# myapp/admin.py
from django.contrib import admin
from .models import (
    Feedback, Category, Dish, Restaurant,
    DishRestaurant, Review, Wishlist
)

admin.site.register(Feedback)
admin.site.register(Category)
admin.site.register(Dish)
admin.site.register(Restaurant)
admin.site.register(DishRestaurant)
admin.site.register(Review)
admin.site.register(Wishlist)
