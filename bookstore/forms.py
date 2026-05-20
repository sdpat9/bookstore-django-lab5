from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

from .models import (
    Book,
    Review,
    Customer,
    UserProfile,
    Order,
    OrderItem,
)


class RegisterForm(UserCreationForm):
    email = forms.EmailField()
    phone = forms.CharField(
        label='Телефон',
        help_text='Формат: +375 (29) XXX-XX-XX'
    )
    birth_date = forms.DateField(
        label='Дата рождения',
        widget=forms.DateInput(attrs={'type': 'date'})
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'phone', 'birth_date', 'password1', 'password2']


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['role', 'phone', 'birth_date']
        widgets = {
            'birth_date': forms.DateInput(attrs={'type': 'date'}),
        }


class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = [
            'title',
            'article',
            'description',
            'category',
            'manufacturer',
            'authors',
            'price',
            'unit',
            'stock_quantity',
            'image',
        ]
        widgets = {
            'authors': forms.CheckboxSelectMultiple(),
        }


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['name', 'rating', 'text']


class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ['full_name', 'city', 'address', 'phone', 'birth_date', 'email']
        widgets = {
            'birth_date': forms.DateInput(attrs={'type': 'date'}),
        }


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['customer', 'delivery_date', 'status', 'promo_code']
        widgets = {
            'delivery_date': forms.DateInput(attrs={'type': 'date'}),
        }


class OrderItemForm(forms.ModelForm):
    class Meta:
        model = OrderItem
        fields = ['book', 'quantity', 'price_at_moment']