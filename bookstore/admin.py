from django.contrib import admin

from .models import (
    UserProfile,
    CompanyInfo,
    NewsArticle,
    FAQ,
    Employee,
    Vacancy,
    Review,
    PromoCode,
    Manufacturer,
    BookCategory,
    Book,
    Author,
    Customer,
    Order,
    OrderItem,
)


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1


class BookInline(admin.TabularInline):
    model = Book.authors.through
    extra = 1


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'article', 'category', 'manufacturer', 'price', 'stock_quantity')
    list_filter = ('category', 'manufacturer')
    search_fields = ('title', 'article', 'description')
    filter_horizontal = ('authors',)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer', 'order_date', 'delivery_date', 'status', 'total_price')
    list_filter = ('status', 'order_date')
    search_fields = ('customer__full_name',)
    inlines = [OrderItemInline]


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'city', 'phone', 'email')
    search_fields = ('full_name', 'city', 'phone')
    list_filter = ('city',)


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('name', 'rating', 'created_at')
    list_filter = ('rating', 'created_at')


@admin.register(PromoCode)
class PromoCodeAdmin(admin.ModelAdmin):
    list_display = ('code', 'discount_percent', 'valid_until', 'is_active')
    list_filter = ('is_active',)


admin.site.register(UserProfile)
admin.site.register(CompanyInfo)
admin.site.register(NewsArticle)
admin.site.register(FAQ)
admin.site.register(Employee)
admin.site.register(Vacancy)
admin.site.register(Manufacturer)
admin.site.register(BookCategory)
admin.site.register(Author)
admin.site.register(OrderItem)