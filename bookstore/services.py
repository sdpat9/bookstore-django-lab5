import base64
import calendar
import statistics
from io import BytesIO
from datetime import datetime

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

import requests
from django.db.models import Sum, Count, F
from django.utils import timezone

from .models import Book, OrderItem, Order


def get_text_calendar(year=None, month=None):
    now = datetime.now()
    year = year or now.year
    month = month or now.month
    return calendar.TextCalendar(firstweekday=0).formatmonth(year, month)


def get_book_statistics():
    prices = list(Book.objects.values_list('price', flat=True))

    if not prices:
        return {
            'count': 0,
            'average_price': 0,
            'median_price': 0,
            'mode_price': 0,
        }

    try:
        mode_price = statistics.mode(prices)
    except statistics.StatisticsError:
        mode_price = 'Нет единственной моды'

    return {
        'count': len(prices),
        'average_price': round(statistics.mean(prices), 2),
        'median_price': round(statistics.median(prices), 2),
        'mode_price': mode_price,
    }


def get_sales_by_category():
    return (
        OrderItem.objects
        .values(category=F('book__category__name'))
        .annotate(total=Sum(F('quantity') * F('price_at_moment')))
        .order_by('-total')
    )


def build_sales_chart_base64():
    data = list(get_sales_by_category())

    labels = [item['category'] for item in data]
    values = [float(item['total']) for item in data]

    if not labels:
        labels = ['Нет данных']
        values = [0]

    plt.figure(figsize=(8, 5))
    plt.bar(labels, values)
    plt.title('Продажи по категориям книг')
    plt.xlabel('Категория')
    plt.ylabel('Сумма продаж')
    plt.xticks(rotation=30, ha='right')
    plt.tight_layout()

    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    plt.close()

    buffer.seek(0)
    image_png = buffer.getvalue()
    return base64.b64encode(image_png).decode('utf-8')


def get_openlibrary_info(title):
    try:
        response = requests.get(
            'https://openlibrary.org/search.json',
            params={'title': title},
            timeout=5
        )
        response.raise_for_status()
        data = response.json()
        docs = data.get('docs', [])[:5]

        return [
            {
                'title': item.get('title'),
                'author': ', '.join(item.get('author_name', [])),
                'first_publish_year': item.get('first_publish_year'),
            }
            for item in docs
        ]
    except requests.RequestException:
        return []


def get_random_quote():
    try:
        response = requests.get('https://api.quotable.io/random', timeout=5)
        response.raise_for_status()
        data = response.json()

        return {
            'content': data.get('content'),
            'author': data.get('author'),
        }
    except requests.RequestException:
        return {
            'content': 'Цитата временно недоступна',
            'author': 'System',
        }