from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Avg, Count
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib import messages
from django.http import Http404
import difflib

from .models import Dish, DishRestaurant, Restaurant, Wishlist, Review, Feedback
from .forms import ReviewForm, FeedbackForm, SignUpForm, WishlistForm

#Basic Landing page
def landing(request):
    return render(request, "myapp/landing.html")

# home page for Top 5 according to review counts
def home(request):
    trending = (
        DishRestaurant.objects
        .annotate(review_count=Count("reviews"))
        .order_by("-review_count")[:5]
    )
    return render(request, "myapp/home.html", {"trending": trending})


#Display Search Results
def search_results(request):
    query = request.GET.get("q", "").strip()
    if not query:
        return render(request, "myapp/search_results.html", {
            "not_found": True,
            "query": query,
            "hints": [],
        })

    # First try exact match on dish name
    dishes = Dish.objects.filter(name__iexact=query)
    if not dishes.exists():
        # Then try case-insensitive containment
        dishes = Dish.objects.filter(name__icontains=query)
    if not dishes.exists():
        # No matches—offer spelling suggestions and use difflib
        all_names = list(Dish.objects.values_list("name", flat=True))
        hints = difflib.get_close_matches(query, all_names, n=3, cutoff=0.6)
        return render(request, "myapp/search_results.html", {
            "not_found": True,
            "query": query,
            "hints": hints,
        })

    dish = dishes.first()
    combos = DishRestaurant.objects.filter(dish=dish)

    # If logged in, gather dish IDs already in the user’s wishlist
    if request.user.is_authenticated:
        wishlist_ids = list(
            Wishlist.objects.filter(user=request.user)
                            .values_list("dish_id", flat=True)
        )
    else:
        wishlist_ids = []

    return render(request, "myapp/search_results.html", {
        "dish": dish,
        "combos": combos,
        "query": query,
        "wishlist_ids": wishlist_ids,
        "hints": [],
    })

#Review page ordered by created_date
def dish_reviews(request, dish_id, rest_id):
    dr = get_object_or_404(DishRestaurant, dish_id=dish_id, restaurant_id=rest_id)
    reviews = dr.reviews.order_by("-created_date")
    avg_rating = reviews.aggregate(avg=Avg("rating"))["avg"]
    if request.method == "POST":
        if not request.user.is_authenticated:
            return redirect("login")
        form = ReviewForm(request.POST, request.FILES)
        if form.is_valid():
            rev = form.save(commit=False)
            rev.user = request.user
            rev.dish_restaurant = dr
            rev.save()
            return redirect("myapp:dish_reviews", dish_id=dish_id, rest_id=rest_id)
    else:
        form = ReviewForm()

    return render(request, "myapp/dish_reviews.html", {
        "dr": dr,
        "reviews": reviews,
        "avg_rating": avg_rating,
        "form": form,
    })

#Signup page
def signup(request):
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("myapp:home")
    else:
        form = SignUpForm()
    return render(request, "myapp/signup.html", {"form": form})

#Feedback Page
@login_required
def feedback(request):
    if request.method == "POST":
        form = FeedbackForm(request.POST)
        if form.is_valid():
            f = form.save(commit=False)
            f.user = request.user
            f.save()
            return redirect("myapp:home")
    else:
        form = FeedbackForm()
    return render(request, "myapp/feedback.html", {"form": form})

#Restaurant List Page
def restaurant_list(request):
    restaurants = Restaurant.objects.all().order_by("name")
    return render(request, "myapp/restaurant_list.html", {"restaurants": restaurants})

#Show each restaurant detail along with dishes served
def restaurant_detail(request, pk):
    restaurant = get_object_or_404(Restaurant, pk=pk)
    dishes = DishRestaurant.objects.filter(restaurant=restaurant)
    return render(request, "myapp/restaurant_detail.html", {
        "restaurant": restaurant,
        "dishes": dishes,
    })


#Profile would consist of wishlist, basic info, delete profile and change the password
@login_required
def profile(request):
    user = request.user
    #Find the wanted dishes for the user
    wishlist_items = Wishlist.objects.filter(user=user).select_related("dish")

    # Get all dish IDs in their wishlist
    dish_ids = [item.dish_id for item in wishlist_items]
    combos = DishRestaurant.objects.filter(dish_id__in=dish_ids).select_related("dish", "restaurant")

    # For each dish_id, just pick the first combo we find
    dish_to_combo = {}
    for combo in combos:
        if combo.dish_id not in dish_to_combo:
            dish_to_combo[combo.dish_id] = combo

    # Build a list of (wishlist_item, combo_or_None)
    paired_wishlist = []
    for item in wishlist_items:
        combo = dish_to_combo.get(item.dish_id)
        paired_wishlist.append((item, combo))

    # Also grab all reviews this user has written
    my_reviews = Review.objects.filter(user=user).select_related(
        "dish_restaurant__dish", "dish_restaurant__restaurant"
    ).order_by("-created_date")

    return render(request, "myapp/profile.html", {
        "paired_wishlist": paired_wishlist,
        "my_reviews": my_reviews,
    })


@login_required
def wishlist_add(request, dish_id):
    dish = get_object_or_404(Dish, pk=dish_id)

    # If already in wishlist, bounce straight back to profile
    if Wishlist.objects.filter(user=request.user, dish=dish).exists():
        return redirect("myapp:profile")

    if request.method == "POST":
        form = WishlistForm(request.POST)
        if form.is_valid():
            comments = form.cleaned_data["comments"]
            Wishlist.objects.create(
                user=request.user,
                dish=dish,
                comments=comments,
            )
            return redirect("myapp:profile")
    else:
        form = WishlistForm()

    return render(request, "myapp/wishlist_add.html", {
        "form": form,
        "dish": dish,
    })


@login_required
def wishlist_remove(request, item_id):
    item = get_object_or_404(Wishlist, pk=item_id, user=request.user)
    item.delete()
    return redirect("myapp:profile")


@login_required
def change_password(request):
    if request.method == "POST":
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, "Password successfully updated.")
            return redirect("myapp:profile")
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = PasswordChangeForm(request.user)

    return render(request, "myapp/change_password.html", {"form": form})


@login_required
def delete_profile(request):
    if request.method == "POST":
        user = request.user
        logout(request)
        user.delete()
        messages.success(request, "Your account has been deleted.")
        return redirect("myapp:home")
    return render(request, "myapp/delete_profile.html")


@login_required
def review_edit(request, pk):
    rev = get_object_or_404(Review, pk=pk)
    if rev.user != request.user:
        raise Http404
    if request.method == "POST":
        form = ReviewForm(request.POST, request.FILES, instance=rev)
        if form.is_valid():
            form.save()
            return redirect("myapp:profile")
    else:
        form = ReviewForm(instance=rev)

    return render(request, "myapp/review_edit.html", {
        "form": form,
        "review": rev,
    })


@login_required
def review_delete(request, pk):
    rev = get_object_or_404(Review, pk=pk)
    if rev.user != request.user:
        raise Http404
    if request.method == "POST":
        rev.delete()
        return redirect("myapp:profile")
    return render(request, "myapp/review_confirm_delete.html", {
        "review": rev,
    })
