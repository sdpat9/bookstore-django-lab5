from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.urls import reverse
from django.utils import timezone

from .validators import validate_belarus_phone, validate_18_plus


class UserProfile(models.Model):
    ROLE_CHOICES = [
        ('CUSTOMER', 'Покупатель'),
        ('EMPLOYEE', 'Сотрудник'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='CUSTOMER')
    phone = models.CharField(max_length=20, validators=[validate_belarus_phone])
    birth_date = models.DateField(validators=[validate_18_plus])

    created_at_utc = models.DateTimeField(default=timezone.now)
    created_at_local = models.DateTimeField(default=timezone.localtime)

    class Meta:
        verbose_name = 'Профиль пользователя'
        verbose_name_plural = 'Профили пользователей'

    def __str__(self):
        return f'{self.user.username} — {self.get_role_display()}'


class CompanyInfo(models.Model):
    name = models.CharField(max_length=150)
    description = models.TextField()
    logo = models.ImageField(upload_to='company/', blank=True, null=True)
    founded_year = models.PositiveIntegerField()
    requisites = models.TextField(blank=True)

    class Meta:
        verbose_name = 'Информация о компании'
        verbose_name_plural = 'Информация о компании'

    def __str__(self):
        return self.name


class NewsArticle(models.Model):
    title = models.CharField(max_length=200)
    short_description = models.CharField(max_length=255)
    content = models.TextField()
    image = models.ImageField(upload_to='news/', blank=True, null=True)
    published_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Новость'
        verbose_name_plural = 'Новости'
        ordering = ['-published_at']

    def __str__(self):
        return self.title


class FAQ(models.Model):
    question = models.CharField(max_length=255)
    answer = models.TextField()
    added_at = models.DateField(default=timezone.now)

    class Meta:
        verbose_name = 'Термин / вопрос'
        verbose_name_plural = 'Словарь терминов и понятий'

    def __str__(self):
        return self.question


class Employee(models.Model):
    full_name = models.CharField(max_length=150)
    position = models.CharField(max_length=100)
    description = models.TextField()
    phone = models.CharField(max_length=20, validators=[validate_belarus_phone])
    email = models.EmailField()
    birth_date = models.DateField(validators=[validate_18_plus])
    photo = models.ImageField(upload_to='employees/', blank=True, null=True)

    class Meta:
        verbose_name = 'Сотрудник'
        verbose_name_plural = 'Сотрудники'

    def __str__(self):
        return self.full_name


class Vacancy(models.Model):
    title = models.CharField(max_length=150)
    description = models.TextField()
    salary = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Вакансия'
        verbose_name_plural = 'Вакансии'

    def __str__(self):
        return self.title


class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    name = models.CharField(max_length=100)
    rating = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    text = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.name}: {self.rating}/5'


class PromoCode(models.Model):
    code = models.CharField(max_length=50, unique=True)
    description = models.TextField()
    discount_percent = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(100)])
    valid_until = models.DateField()
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Промокод'
        verbose_name_plural = 'Промокоды и купоны'

    def __str__(self):
        return self.code


class Manufacturer(models.Model):
    name = models.CharField(max_length=150)
    country = models.CharField(max_length=100)
    website = models.URLField(blank=True)

    class Meta:
        verbose_name = 'Изготовитель'
        verbose_name_plural = 'Изготовители'

    def __str__(self):
        return self.name


class BookCategory(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    class Meta:
        verbose_name = 'Вид товара'
        verbose_name_plural = 'Виды товаров'

    def __str__(self):
        return self.name


class Book(models.Model):
    title = models.CharField(max_length=200)
    article = models.CharField(max_length=50, unique=True)
    description = models.TextField()
    category = models.ForeignKey(BookCategory, on_delete=models.PROTECT, related_name='books')
    manufacturer = models.ForeignKey(Manufacturer, on_delete=models.PROTECT, related_name='books')
    authors = models.ManyToManyField('Author', related_name='books')
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    unit = models.CharField(max_length=30, default='шт.')
    stock_quantity = models.PositiveIntegerField(default=0)
    image = models.ImageField(upload_to='books/', blank=True, null=True)
    created_at_utc = models.DateTimeField(default=timezone.now)
    created_at_local = models.DateTimeField(default=timezone.localtime)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Книга'
        verbose_name_plural = 'Книги'
        ordering = ['title']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('book_detail', kwargs={'pk': self.pk})


class Author(models.Model):
    full_name = models.CharField(max_length=150)
    birth_year = models.PositiveIntegerField(blank=True, null=True)

    class Meta:
        verbose_name = 'Автор'
        verbose_name_plural = 'Авторы'

    def __str__(self):
        return self.full_name


class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='customer')
    full_name = models.CharField(max_length=150)
    city = models.CharField(max_length=100)
    address = models.CharField(max_length=255)
    phone = models.CharField(max_length=20, validators=[validate_belarus_phone])
    birth_date = models.DateField(validators=[validate_18_plus])
    email = models.EmailField()

    class Meta:
        verbose_name = 'Клиент'
        verbose_name_plural = 'Клиенты'

    def __str__(self):
        return self.full_name


class Order(models.Model):
    STATUS_CHOICES = [
        ('NEW', 'Новый'),
        ('PAID', 'Оплачен'),
        ('DELIVERED', 'Доставлен'),
        ('CANCELLED', 'Отменён'),
    ]

    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='orders')
    books = models.ManyToManyField(Book, through='OrderItem', related_name='orders')
    order_date = models.DateTimeField(default=timezone.now)
    delivery_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='NEW')
    promo_code = models.ForeignKey(PromoCode, on_delete=models.SET_NULL, blank=True, null=True)

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'
        ordering = ['-order_date']

    def __str__(self):
        return f'Заказ №{self.id}'

    @property
    def total_price(self):
        total = sum(item.total_price for item in self.items.all())

        if self.promo_code and self.promo_code.is_active:
            total -= total * self.promo_code.discount_percent / 100

        return round(total, 2)


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    book = models.ForeignKey(Book, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    price_at_moment = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        verbose_name = 'Позиция заказа'
        verbose_name_plural = 'Позиции заказа'

    @property
    def total_price(self):
        return self.quantity * self.price_at_moment

    def __str__(self):
        return f'{self.book.title} × {self.quantity}'