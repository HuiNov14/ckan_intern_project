from flask import request, url_for
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
        {"endpoint": "tracking_blueprint.resource_dashboard", "label": "All Statistics"},
        {"endpoint": "tracking_blueprint.statistical_org", "label": "Organization Statistics"},
        {"endpoint": "tracking_blueprint.statistical_field", "label": "Group Statistics"},
        {"endpoint": "tracking_blueprint.statistical_datatypes", "label": "Datatypes Statistics"},
        {"endpoint": "tracking_blueprint.statistical_tracking", "label": "Tracking Statistics"},
        {"endpoint": "tracking_blueprint.statistical_api", "label": "API Statistics"},
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
    
    
    
def get_breadcrumb_links():
    return [
        {"url": "/dashboard/statistical/resource_dashboard", "label": "Resource Statistics"},
    ]


def get_statistical_cards():
    return [
        {
            "url": "tracking_blueprint.statistical_org",
            "img_src": "/1.png",
            "title": "Organization Statistics",
            "description": "This is a statistical chart of data belonging to an organization.",
        },
        {
            "url": "tracking_blueprint.statistical_field",
            "img_src": "/2.png",
            "title": "Group Statistics",
            "description": "This is a statistical chart of data in a field.",
        },
        {
            "url": "tracking_blueprint.statistical_datatypes",
            "img_src": "/3.png",
            "title": "Datatypes Statistics",
            "description": "This is a statistical chart of the number of data types.",
        },
        {
            "url": "tracking_blueprint.statistical_tracking",
            "img_src": "/4.png",
            "title": "Tracking Statistics",
            "description": "This is a statistical chart that tracks views, downloads of data.",
        },
        {
            "url": "tracking_blueprint.statistical_api",
            "img_src": "/4.png",
            "title": "API Statistics",
            "description": "This is a statistical chart that tracks views, downloads of data.",
        },
    ]

def get_chart_type():
    return [
        {"value": "bar", "label": "Bar"},
        {"value": "line", "label": "Line"},
    ]