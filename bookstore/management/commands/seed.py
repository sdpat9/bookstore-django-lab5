from datetime import date, timedelta

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone

from bookstore.models import (
    CompanyInfo,
    NewsArticle,
    FAQ,
    Employee,
    Vacancy,
    PromoCode,
    Manufacturer,
    BookCategory,
    Author,
    Book,
    Customer,
    Order,
    OrderItem,
    Review,
)


class Command(BaseCommand):
    help = 'Заполняет базу тестовыми данными для лабораторной работы'

    def handle(self, *args, **options):
        CompanyInfo.objects.get_or_create(
            name='BookStore',
            defaults={
                'description': 'BookStore — интернет-магазин художественной, учебной и деловой литературы.',
                'founded_year': 2020,
                'requisites': 'ООО BookStore, УНП 123456789, г. Минск, пр. Независимости, 1',
            }
        )

        categories = []
        for name in [
            'Фантастика', 'Детективы', 'Романы', 'Программирование', 'Бизнес',
            'Психология', 'История', 'Наука', 'Учебники', 'Комиксы'
        ]:
            category, _ = BookCategory.objects.get_or_create(
                name=name,
                defaults={'description': f'Категория книг: {name}'}
            )
            categories.append(category)

        manufacturers = []
        for i, name in enumerate([
            'Эксмо', 'АСТ', 'Питер', 'Манн, Иванов и Фербер', 'Бомбора',
            'O’Reilly', 'No Starch Press', 'Просвещение', 'Альпина', 'Азбука'
        ], start=1):
            manufacturer, _ = Manufacturer.objects.get_or_create(
                name=name,
                defaults={
                    'country': 'Беларусь' if i % 2 == 0 else 'Россия',
                    'website': 'https://example.com',
                }
            )
            manufacturers.append(manufacturer)

        authors = []
        for name in [
            'Джордж Оруэлл', 'Рэй Брэдбери', 'Стив Макконнелл', 'Роберт Мартин',
            'Фёдор Достоевский', 'Агата Кристи', 'Айзек Азимов', 'Стивен Кинг',
            'Михаил Булгаков', 'Дж. К. Роулинг'
        ]:
            author, _ = Author.objects.get_or_create(
                full_name=name,
                defaults={'birth_year': 1900}
            )
            authors.append(author)

        books = []
        for i in range(10):
            book, _ = Book.objects.get_or_create(
                article=f'BOOK-{i + 1:03}',
                defaults={
                    'title': f'Книга {i + 1}',
                    'description': f'Описание книги {i + 1}. Подходит для демонстрации лабораторной работы.',
                    'category': categories[i],
                    'manufacturer': manufacturers[i],
                    'price': 20 + i * 3,
                    'unit': 'шт.',
                    'stock_quantity': 10 + i,
                }
            )
            book.authors.set([authors[i]])
            books.append(book)

        for i in range(10):
            NewsArticle.objects.get_or_create(
                title=f'Новость {i + 1}',
                defaults={
                    'short_description': f'Краткое описание новости {i + 1}.',
                    'content': f'Полный текст новости {i + 1}. Здесь размещается информация о книжном магазине.',
                }
            )

        for i in range(10):
            FAQ.objects.get_or_create(
                question=f'Термин {i + 1}',
                defaults={
                    'answer': f'Описание термина {i + 1}.',
                    'added_at': timezone.now().date(),
                }
            )

        for i in range(10):
            Employee.objects.get_or_create(
                email=f'employee{i + 1}@bookstore.by',
                defaults={
                    'full_name': f'Сотрудник {i + 1}',
                    'position': 'Менеджер',
                    'description': 'Консультирует покупателей и работает с заказами.',
                    'phone': f'+375 (29) 100-00-{i:02}',
                    'birth_date': date(1990, 1, 1),
                }
            )

        for i in range(10):
            Vacancy.objects.get_or_create(
                title=f'Вакансия {i + 1}',
                defaults={
                    'description': 'Описание вакансии книжного магазина.',
                    'salary': 1000 + i * 100,
                    'is_active': i % 2 == 0,
                }
            )

        for i in range(10):
            PromoCode.objects.get_or_create(
                code=f'BOOK{i + 1}',
                defaults={
                    'description': f'Промокод на скидку {i + 1}%',
                    'discount_percent': min(i + 1, 50),
                    'valid_until': timezone.now().date() + timedelta(days=30 + i),
                    'is_active': i % 2 == 0,
                }
            )

        customers = []
        for i in range(10):
            user, _ = User.objects.get_or_create(
                username=f'customer{i + 1}',
                defaults={
                    'email': f'customer{i + 1}@mail.com',
                }
            )
            user.set_password('password123')
            user.save()

            customer, _ = Customer.objects.get_or_create(
                user=user,
                defaults={
                    'full_name': f'Клиент {i + 1}',
                    'city': 'Минск',
                    'address': f'Улица Книжная, дом {i + 1}',
                    'phone': f'+375 (29) 200-00-{i:02}',
                    'birth_date': date(1995, 1, 1),
                    'email': f'customer{i + 1}@mail.com',
                }
            )
            customers.append(customer)

        for i in range(10):
            order, _ = Order.objects.get_or_create(
                customer=customers[i],
                delivery_date=timezone.now().date() + timedelta(days=i + 1),
                defaults={
                    'status': 'PAID',
                    'promo_code': PromoCode.objects.filter(is_active=True).first(),
                }
            )

            OrderItem.objects.get_or_create(
                order=order,
                book=books[i],
                defaults={
                    'quantity': i + 1,
                    'price_at_moment': books[i].price,
                }
            )

        admin_user = User.objects.filter(is_superuser=True).first()

        if admin_user:
            for i in range(10):
                Review.objects.get_or_create(
                    user=admin_user,
                    name=f'Покупатель {i + 1}',
                    text=f'Отзыв {i + 1}. Хороший магазин, удобный каталог.',
                    defaults={
                        'rating': (i % 5) + 1,
                    }
                )

        self.stdout.write(self.style.SUCCESS('База успешно заполнена тестовыми данными.'))