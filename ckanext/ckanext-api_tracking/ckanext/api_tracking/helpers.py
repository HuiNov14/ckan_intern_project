from flask import request, url_for
from flask_babel import gettext as _
import hashlib
import six
import re
from ckan.types import CKANApp
import ckan.model.meta as meta
import ckan.model as model

def generate_user_key(environ):
    try:
        user_agent = environ.get('HTTP_USER_AGENT', 'unknown')
        remote_addr = environ.get('REMOTE_ADDR', 'unknown')
        accept_language = environ.get('HTTP_ACCEPT_LANGUAGE', '')
        accept_encoding = environ.get('HTTP_ACCEPT_ENCODING', '')

        key = ''.join([user_agent, remote_addr, accept_language, accept_encoding])
        return hashlib.md5(six.ensure_binary(key)).hexdigest()
    except Exception as e:
        CKANApp.logger.error(f"Error generating user key: {e}")
        return None

def get_data_type(url):
    try:
        if check_resource(url):
            return 'resource'
        elif check_download(url):
            return 'download'
        elif check_dataset(url):
            return 'page'
        return None
    except Exception as e:
        CKANApp.logger.error(f"Error getting data type: {e}")
        return None

def check_dataset(url):
    try:
        pattern1 = r'^/dataset/([^/]+)$'
        match1 = re.match(pattern1, url)
            
        if match1:
            package_name = match1.group(1) 
            dataset = meta.Session.query(model.Package
                                         ).filter(model.Package.name == package_name).first()                
            return dataset is not None
        
    except Exception as e:
        CKANApp.logger.error(f"Error checking dataset: {e}")
            
    return False

def check_resource(url):
    try:
        pattern = r'^/dataset/([^/]+)/resource/([^/]+)$'
        match = re.match(pattern, url)
        if match:
            resource_id = match.group(2)
            package_name = url.split('/resource/')[0].split('/')[-1]
            resource = meta.Session.query(model.Resource).join(
                model.Package,  
                model.Resource.package_id == model.Package.id
            ).filter(
                model.Resource.id == resource_id,
                model.Package.name == package_name,
            ).first()
            print(resource)
            return resource is not None
    except Exception as e:
        CKANApp.logger.error(f"Error checking resource: {e}")
        
    return False

def check_download(url):
    try:
        pattern = r'^(.*/resource/([^/]+)/download/.*)'
        match = re.match(pattern, url)
        if match:
            resource_id = match.group(2)
            package_id = url.split('/resource/')[0].split('/')[-1]
            resource_name = url.split('/download/')[1]
            resource = meta.Session.query(model.Resource).filter(
                model.Resource.id == resource_id,
                model.Resource.package_id == package_id,
                model.Resource.url == resource_name
            ).first()

            return resource is not None
    except Exception as e:
        CKANApp.logger.error(f"Error checking resource: {e}")
        
    return False


def get_statistics_options():
    # Lấy URL hiện tại
    current_url = request.path

    # Danh sách các tùy chọn với endpoint
    options = [
        {"endpoint": "tracking_blueprint.resource_dashboard", "label": _("All Statistics")},
        {"endpoint": "tracking_blueprint.statistical_org", "label": _("Organization Statistics")},
        {"endpoint": "tracking_blueprint.statistical_field", "label": _("Group Statistics")},
        {"endpoint": "tracking_blueprint.statistical_datatypes", "label": _("Datatypes Statistics")},
        {"endpoint": "tracking_blueprint.statistical_tracking", "label": _("Tracking Statistics")},
        {"endpoint": "tracking_blueprint.statistical_api", "label": _("API Statistics")},
        {"endpoint": "tracking_blueprint.statistical_resource", "label": _("Resource statistics chart")},
    ]

    # Tạo URL từ endpoint và đánh dấu 'selected'
    for option in options:
        try:
            option["value"] = url_for(option["endpoint"])
            option["selected"] = option["value"] == current_url
        except Exception:
            # Xử lý nếu endpoint không tồn tại
            option["value"] = None
            option["selected"] = False

    # Loại bỏ các tùy chọn không hợp lệ (không tạo được URL)
    options = [option for option in options if option["value"]]

    return options
    
def get_statistics_options_user():
    # Lấy URL hiện tại
    current_url = request.path

    # Danh sách các tùy chọn với endpoint
    options = [
        {"endpoint": "tracking_blueprint.user_dashboard", "label": _("All Statistics User")},
        {"endpoint": "tracking_blueprint.user_login_statistical", "label": _("User Login Activity Statistics")},
        {"endpoint": "tracking_blueprint.new_user_statistical", "label": _("New User Statistics")},
        {"endpoint": "tracking_blueprint.statistical_user_time", "label": _("User Time Statistics")},
    ]

    # Tạo URL từ endpoint và đánh dấu 'selected'
    for option in options:
        try:
            option["value"] = url_for(option["endpoint"])
            option["selected"] = option["value"] == current_url
        except Exception:
            # Xử lý nếu endpoint không tồn tại
            option["value"] = None
            option["selected"] = False

    # Loại bỏ các tùy chọn không hợp lệ (không tạo được URL)
    options = [option for option in options if option["value"]]

    return options
    

def get_statistical_cards_resource():
    return [
    {
        "url": "tracking_blueprint.statistical_org",
        "img_src": "/image_org.jpg",
        "title": _("Organization Statistics"),
        "description": _("This is a statistical chart of data belonging to an organization."),
    },
    {
        "url": "tracking_blueprint.statistical_field",
        "img_src": "/image_group.jpg",
        "title": _("Group Statistics"),
        "description": _("This is a statistical chart of data in a field."),
    },
    {
        "url": "tracking_blueprint.statistical_datatypes",
        "img_src": "/image_datatypes.jpg",
        "title": _("Datatypes Statistics"),
        "description": _("This is a statistical chart of the number of data types."),
    },
    {
        "url": "tracking_blueprint.statistical_tracking",
        "img_src": "/image_tracking.jpg",
        "title": _("Tracking Statistics"),
        "description": _("This is a statistical chart that tracks views, downloads of data."),
    },
    {
        "url": "tracking_blueprint.statistical_api",
        "img_src": "/image_api.jpg",
        "title": _("API Statistics"),
        "description": _("This is a statistical chart that tracks views, downloads of data."),
    },
    {
        "url": "tracking_blueprint.statistical_resource",
        "img_src": "/image_resource.jpg",
        "title": _("Resource statistics chart"),
        "description": _("This is a chart of data statistics over time."),
    },
]
    
def get_statistical_cards_user():
    return [
        {
            "url": "tracking_blueprint.new_user_statistical",
            "img_src": "/image_new_user.jpg",
            "title": _("New User Statistics"),
            "description": _("Statistics of new users (new accounts created) over time"),
        },
        {
            "url": "tracking_blueprint.user_login_statistical",
            "img_src": "/image_login_show_activity.jpg",
            "title": _("User Login Activity Statistics"),
            "description": _("Statistics of user logins over time"),
        },
        {
            "url": "tracking_blueprint.statistical_user_time",
            "img_src": "/image_user_time.jpg",
            "title": _("User Time Statistics"),
            "description": _("Statistics of user times over time"),
        },
    ]

def get_chart_type():
    return [
        {"value": "bar", "label": _("Bar")},
        {"value": "line", "label": _("Line")},
    ]
    
def get_validation_error_messages():
    """Trả về các thông báo lỗi đã được dịch."""
    return {
        'start_date_invalid': _('Please enter a valid start date.'),
        'end_date_invalid': _('Please enter a valid end date.'),
        'start_date_after_end_date': _('Start date must be earlier than or equal to end date.'),
        'end_date_before_start_date': _('End date must be later than or equal to start date.')
    }
    
def get_info_name_static_tracking():
    return {
        'x': _('Date'),
        'y': _('Count'),
        'from': _('Date Range: From'),
        'to': _('To'),
        'total_package_view': _('Total Package Views:'),
        'package_view': _('Package Views'),
        'resource_download': _('Resource Downloads'),
        'resource_view': _('Resource Views'),
        'resource_name': _('Resource Name'),
    }