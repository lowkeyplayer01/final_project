# myapp/urls.py
from django.urls import path
from . import views

app_name = "myapp"

urlpatterns = [
    path('', views.landing, name='landing'),
    path('home/', views.home, name='home'),
    path('search/',  views.search_results,  name='search_results'),

    path('restaurant/<int:pk>/', views.restaurant_detail, name='restaurant_detail'),
    path('restaurants/', views.restaurant_list, name='restaurant_list'),

    path('dish/<int:dish_id>/restaurant/<int:rest_id>/',views.dish_reviews,name='dish_reviews'),
    path('reviews/', views.dish_reviews, name='dish_reviews'),
    path('review/<int:pk>/edit/',   views.review_edit,   name='review_edit'),
    path('review/<int:pk>/delete/', views.review_delete, name='review_delete'),

    path('feedback/', views.feedback, name='feedback'),

    path('signup/', views.signup, name='signup'),

    path('wishlist/add/<int:dish_id>/', views.wishlist_add, name='wishlist_add'),
    path('wishlist/remove/<int:item_id>/', views.wishlist_remove, name='wishlist_remove'),

    path('profile/', views.profile, name='profile'),
    path('profile/change_password/', views.change_password, name='change_password'),
    path('profile/delete/', views.delete_profile, name='delete_profile'),

]
