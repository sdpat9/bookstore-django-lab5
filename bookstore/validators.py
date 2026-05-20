import re
from datetime import date
from django.core.exceptions import ValidationError


PHONE_PATTERN = r'^\+375 \((29|25|33|44)\) \d{3}-\d{2}-\d{2}$'


def validate_belarus_phone(value):
    if not re.match(PHONE_PATTERN, value):
        raise ValidationError('Телефон должен быть в формате +375 (29) XXX-XX-XX')


def validate_18_plus(value):
    today = date.today()
    age = today.year - value.year - ((today.month, today.day) < (value.month, value.day))

    if age < 18:
        raise ValidationError('Возраст должен быть 18+')