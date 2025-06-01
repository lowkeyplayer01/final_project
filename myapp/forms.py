from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import Feedback, Review, DishRestaurant, Dish, Restaurant, Wishlist


# 1
class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ['suggestions']
        widgets = {
            'suggestions': forms.Textarea(attrs={
                'rows': 5,
                'placeholder': 'Write your feedback…',
            }),
        }
        error_messages = {
            'suggestions': {
                'required': "Feedback cannot be blank.",
                'min_length': "Please provide at least 20 characters.",
                'max_length': "Feedback is too long (1000 characters max).",
            }
        }

    suggestions = forms.CharField(min_length=20, max_length=1000)

    def clean_suggestions(self):
        text = self.cleaned_data['suggestions'].strip()
        if not text:
            raise ValidationError("Feedback cannot be blank or only whitespace.")
        for bad in ('shit', 'fuck', 'asshole', 'dickhead'):
            if bad in text.lower():
                raise ValidationError("Please help us build a friendly community :)")
        return text


# 2
class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'price_paid', 'description', 'photo']
        widgets = {
            'description': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': 'Your thoughts…'
            }),
        }
        labels = {
            'rating': 'Rating',
            'price_paid': 'Price Paid',
            'description': 'Review',
            'photo': 'Photo (optional)',
        }

    def clean_description(self):
        text = self.cleaned_data['description'].strip()
        if not text:
            raise ValidationError("Review cannot be blank or only whitespace.")
        for bad in ('shit', 'fuck', 'asshole', 'dickhead'):
            if bad in text.lower():
                raise ValidationError("Please help us build a friendly community :)")
        return text

    def clean_photo(self):
        photo = self.cleaned_data.get('photo')
        if not photo:
            return photo
        max_size = 1 * 1024 * 1024  # 1 MB
        if photo.size > max_size:
            raise ValidationError("Image size must be under 1 MB.")
        if photo.content_type not in ('image/jpeg', 'image/png'):
            raise ValidationError("Only JPEG or PNG images are allowed.")
        return photo

# 3
class DishRestaurantForm(forms.ModelForm):
    class Meta:
        model = DishRestaurant
        fields = ['restaurant', 'dish', 'local_name']

    def clean(self):
        cleaned = super().clean()
        restaurant = cleaned.get('restaurant')
        dish = cleaned.get('dish')
        if restaurant and dish:
            if DishRestaurant.objects.filter(restaurant=restaurant, dish=dish).exists():
                self.add_error('dish', "This dish is already listed for that restaurant.")
        return cleaned


# 4
class WishlistForm(forms.ModelForm):
    class Meta:
        model = Wishlist
        fields = ['comments']
        widgets = {
            'comments': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'Any notes…',
            }),
        }
        labels = {
            'comments': 'Notes (optional)',
        }



# 5
class SignUpForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password1', 'password2']

    def clean_email(self):
        email = self.cleaned_data['email'].strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise ValidationError("A user with that email already exists.")
        return email

    def clean_password1(self):
        pwd = self.cleaned_data.get('password1', '')
        if len(pwd) < 8:
            raise ValidationError("Password must be at least 8 characters.")
        if not any(ch.isdigit() for ch in pwd):
            raise ValidationError("Password must contain at least one digit.")
        if not any(ch.isupper() for ch in pwd):
            raise ValidationError("Password must contain at least one uppercase letter.")
        return pwd

    def clean(self):
        cleaned = super().clean()
        username = cleaned.get('username', '')
        email = cleaned.get('email', '')
        if username and email:
            local_part = email.split('@')[0].lower()
            if username.lower() == local_part:
                raise ValidationError("Username should not match the part of your email before '@'.")
        return cleaned
