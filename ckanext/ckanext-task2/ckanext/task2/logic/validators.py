# validators.py
import datetime
from ckan.plugins import toolkit

def validate_date(value):
    try:
        datetime.datetime.strptime(value, '%Y-%m-%d')
        return value
    except ValueError:
        raise toolkit.Invalid('Date format should be YYYY-MM-DD')

def validate_month(value):
    try:
        datetime.datetime.strptime(value, '%Y-%m')
        return value
    except ValueError:
        raise toolkit.Invalid('Date format should be YYYY-MM')

def validate_bool(value):
    if value not in [True, False]:
        raise ValueError("include_resources should be True or False")
    return value