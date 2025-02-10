from ckan.plugins.toolkit import ValidationError
import ckan.plugins.toolkit as tk
import datetime
from ckan.lib.navl.dictization_functions import Invalid
from gettext import gettext as _


def max_30_days_validator(value):
    if value > 15 or value <= 0:
        raise Invalid(_("The 'recent_active_days' value cannot exceed 30 days and less than 0."))
    return value


def validate_date_range(value, context):
    """ Validator kiểm tra start_date phải nhỏ hơn hoặc bằng end_date """
    data_dict = context.get('data', {})

    start_date = data_dict.get("start_date")
    end_date = data_dict.get("end_date")

    if start_date and end_date:
        try:
            start_date_dt = datetime.datetime.strptime(start_date, "%Y-%m-%d")
            end_date_dt = datetime.datetime.strptime(end_date, "%Y-%m-%d")
        except ValueError:
            raise tk.Invalid(tk._("Ngày không đúng định dạng (YYYY-MM-DD)"))

        if start_date_dt > end_date_dt:
            raise tk.Invalid(tk._("Ngày bắt đầu phải nhỏ hơn hoặc bằng ngày kết thúc."))

    return value

