from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.db.models import Q, Sum, Count, F
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone

from .forms import (
    RegisterForm,
    BookForm,
    ReviewForm,
    CustomerForm,
    OrderForm,
)
from .models import (
    UserProfile,
    CompanyInfo,
    NewsArticle,
    FAQ,
    Employee,
    Vacancy,
    Review,
    PromoCode,
    Book,
    Customer,
    Order,
    OrderItem,
)
from .services import (
    get_text_calendar,
    get_book_statistics,
    build_sales_chart_base64,
    get_openlibrary_info,
    get_random_quote,
)


def is_employee_or_admin(user):
    if user.is_superuser:
        return True

    return hasattr(user, 'profile') and user.profile.role == 'EMPLOYEE'


def home(request):
    latest_news = NewsArticle.objects.first()
    quote = get_random_quote()

    return render(request, 'bookstore/home.html', {
        'latest_news': latest_news,
        'quote': quote,
    })


def about(request):
    company = CompanyInfo.objects.first()
    return render(request, 'bookstore/about.html', {'company': company})


def news_list(request):
    news = NewsArticle.objects.all()
    return render(request, 'bookstore/news_list.html', {'news': news})


def news_detail(request, pk):
    article = get_object_or_404(NewsArticle, pk=pk)
    return render(request, 'bookstore/news_detail.html', {'article': article})


def faq_list(request):
    faqs = FAQ.objects.all()
    return render(request, 'bookstore/faq_list.html', {'faqs': faqs})


def contacts(request):
    employees = Employee.objects.all()
    return render(request, 'bookstore/contacts.html', {'employees': employees})


def privacy_policy(request):
    return render(request, 'bookstore/privacy_policy.html')


def vacancy_list(request):
    vacancies = Vacancy.objects.filter(is_active=True)
    return render(request, 'bookstore/vacancy_list.html', {'vacancies': vacancies})


def promocode_list(request):
    active_promos = PromoCode.objects.filter(is_active=True)
    archive_promos = PromoCode.objects.filter(is_active=False)

    return render(request, 'bookstore/promocode_list.html', {
        'active_promos': active_promos,
        'archive_promos': archive_promos,
    })


def review_list(request):
    reviews = Review.objects.all()
    return render(request, 'bookstore/review_list.html', {'reviews': reviews})


@login_required
def review_create(request):
    if request.method == 'POST':
        form = ReviewForm(request.POST)

        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user
            review.save()
            messages.success(request, 'Отзыв добавлен')
            return redirect('review_list')
    else:
        form = ReviewForm(initial={
            'name': request.user.username,
        })

    return render(request, 'bookstore/review_form.html', {'form': form})


def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)

        if form.is_valid():
            user = form.save(commit=False)
            user.email = form.cleaned_data['email']
            user.save()

            UserProfile.objects.create(
                user=user,
                role='CUSTOMER',
                phone=form.cleaned_data['phone'],
                birth_date=form.cleaned_data['birth_date'],
            )

            login(request, user)
            messages.success(request, 'Регистрация выполнена')
            return redirect('home')
    else:
        form = RegisterForm()

    return render(request, 'registration/register.html', {'form': form})


def book_list(request):
    books = Book.objects.select_related('category', 'manufacturer').prefetch_related('authors')

    query = request.GET.get('q', '')
    sort = request.GET.get('sort', 'title')

    if query:
        books = books.filter(
            Q(title__icontains=query) |
            Q(article__icontains=query) |
            Q(description__icontains=query) |
            Q(category__name__icontains=query) |
            Q(manufacturer__name__icontains=query)
        )

    allowed_sorts = ['title', '-title', 'price', '-price', 'stock_quantity', '-stock_quantity']

    if sort in allowed_sorts:
        books = books.order_by(sort)

    return render(request, 'bookstore/book_list.html', {
        'books': books,
        'query': query,
        'sort': sort,
    })


def book_detail(request, pk):
    book = get_object_or_404(Book, pk=pk)
    api_books = get_openlibrary_info(book.title)

    return render(request, 'bookstore/book_detail.html', {
        'book': book,
        'api_books': api_books,
    })


@login_required
@user_passes_test(is_employee_or_admin)
def book_create(request):
    if request.method == 'POST':
        form = BookForm(request.POST, request.FILES)

        if form.is_valid():
            form.save()
            messages.success(request, 'Книга добавлена')
            return redirect('book_list')
    else:
        form = BookForm()

    return render(request, 'bookstore/book_form.html', {'form': form})


@login_required
@user_passes_test(is_employee_or_admin)
def book_update(request, pk):
    book = get_object_or_404(Book, pk=pk)

    if request.method == 'POST':
        form = BookForm(request.POST, request.FILES, instance=book)

        if form.is_valid():
            form.save()
            messages.success(request, 'Книга обновлена')
            return redirect('book_detail', pk=book.pk)
    else:
        form = BookForm(instance=book)

    return render(request, 'bookstore/book_form.html', {'form': form})


@login_required
@user_passes_test(is_employee_or_admin)
def book_delete(request, pk):
    book = get_object_or_404(Book, pk=pk)

    if request.method == 'POST':
        book.delete()
        messages.success(request, 'Книга удалена')
        return redirect('book_list')

    return render(request, 'bookstore/book_confirm_delete.html', {'book': book})


@login_required
def profile(request):
    orders = Order.objects.none()

    if hasattr(request.user, 'customer'):
        orders = Order.objects.filter(customer=request.user.customer)

    return render(request, 'bookstore/profile.html', {
        'orders': orders,
    })


@login_required
@user_passes_test(is_employee_or_admin)
def customer_list(request):
    customers = Customer.objects.all().order_by('full_name')
    return render(request, 'bookstore/customer_list.html', {'customers': customers})


@login_required
@user_passes_test(is_employee_or_admin)
def customer_create(request):
    if request.method == 'POST':
        form = CustomerForm(request.POST)

        if form.is_valid():
            form.save()
            messages.success(request, 'Клиент добавлен')
            return redirect('customer_list')
    else:
        form = CustomerForm()

    return render(request, 'bookstore/customer_form.html', {'form': form})


@login_required
@user_passes_test(is_employee_or_admin)
def order_list(request):
    orders = Order.objects.select_related('customer', 'promo_code').all()
    return render(request, 'bookstore/order_list.html', {'orders': orders})


@login_required
@user_passes_test(is_employee_or_admin)
def order_create(request):
    if request.method == 'POST':
        form = OrderForm(request.POST)

        if form.is_valid():
            form.save()
            messages.success(request, 'Заказ создан')
            return redirect('order_list')
    else:
        form = OrderForm()

    return render(request, 'bookstore/order_form.html', {'form': form})


@login_required
@user_passes_test(is_employee_or_admin)
def statistics_view(request):
    stats = get_book_statistics()
    sales_by_category = OrderItem.objects.values(
        'book__category__name'
    ).annotate(
        total_quantity=Sum('quantity'),
        total_sum=Sum(F('quantity') * F('price_at_moment'))
    ).order_by('-total_sum')

    chart = build_sales_chart_base64()
    text_calendar = get_text_calendar()
    current_utc = timezone.now()
    current_local = timezone.localtime(current_utc)

    return render(request, 'bookstore/statistics.html', {
        'stats': stats,
        'sales_by_category': sales_by_category,
        'chart': chart,
        'text_calendar': text_calendar,
        'current_utc': current_utc,
        'current_local': current_local,
    })