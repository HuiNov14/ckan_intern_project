from encodings import undefined
import json
import requests
from math import log
from typing import Any
from flask import Blueprint, request
import ckan.plugins.toolkit as toolkit
from ckan.common import config
import ckanext.api_tracking.logic.auth as auth  
from datetime import datetime, timedelta
from ckan import logic
import ckan.lib.base as base
from ckan.lib.helpers import helper_functions as h
from ckan.lib.helpers import Page
from datetime import date
from.logic.validators import validate_date_range
from .helpers import get_validation_error_messages,get_info_name_static_tracking,color_chart_datatypes,get_info_chart_name_api

# Blueprint for tracking
dashboard = Blueprint('tracking_blueprint', __name__, url_prefix=u'/dashboard/')


def resource_dashboard():
        return base.render('user/resource_dashboard.html')

def user_dashboard():
        return base.render('user/user_dashboard.html')
    
#Dashboard/statistical
def statistical():

    try:
        logic.check_access('user_check', {})
    except logic.NotAuthorized:
        return base.abort(403, toolkit._('Need to be system administrator to administer'))

    return base.render('user/dashboard_statistical.html')

def aggregate_package_views(urls_and_counts):
    """Aggregate package views for each unique package."""
    aggregated_data = {}

    # Loop through the tracking data
    for url in urls_and_counts:
        user_name = url['user_name']
        for tracking in url['tracking']:
            date_time = tracking['date']
            package_name = tracking['package']
            package_id = tracking['package_id']
            package_views = tracking['package_view']
            title = tracking['title']
            include_resources = tracking.get('include_resources', [])
            
            if not package_id:
                continue
            
            # Convert date_time (if it is a date object) to string (optional: you can use a different format)
            if isinstance(date_time, date):
                date_time = date_time.strftime('%Y-%m-%d')  # Chuyển đổi thành chuỗi ngày YYYY-MM-DD

            # If package is already in the aggregated data, sum the views
            if package_name in aggregated_data:
                aggregated_data[package_name]['package_view'] += package_views
                aggregated_data[package_name]['include_resources'].extend(include_resources)
            else:
                aggregated_data[package_name] = {
                    'package': package_name,
                    'package_view': package_views,
                    'title': title,
                    'user_name': user_name,
                    'include_resources': include_resources,
                    'package_id': package_id,
                    'date_time': date_time,
                }
    

    # Convert the aggregated data back to a list for rendering
    return list(aggregated_data.values())



##Dashboard/statistical/statiscal_tracking
def statistical_tracking():
    today = datetime.today().date()     
    day_tracking_default = today - timedelta(days=int(config.get('ckan.day_default')))
    
    start_date = request.form.get('start_date', str(day_tracking_default))  
    end_date = request.form.get('end_date', str(today))  
    package_name = request.form.getlist('package_name') or [""] 
    user_name = request.form.getlist('user_name') or [""]
    include_resources = request.form.get('include_resources') == 'on'  

    try:
        action = 'tracking_by_user'
        urls_and_counts = logic.get_action(action)(data_dict={
            u'user_name': user_name,
            u'start_date': start_date,
            u'end_date': end_date,
            u'package_name': package_name,
            u'include_resources': True,
        }) 

    except logic.NotAuthorized:
        return base.abort(403, toolkit._('Need to be system administrator to administer'))
    
    error_messages = get_validation_error_messages()
    name_static_tracking = get_info_name_static_tracking()
    
    aggregated_urls_and_counts = json.dumps(aggregate_package_views(urls_and_counts))
    
    dataset_alls = logic.get_action('package_list')(data_dict={})
    user_all= logic.get_action('user_list')(data_dict={})
    
    extra_vars: dict[str, Any] = {
        u'data': urls_and_counts,
        u'urls_and_counts': aggregated_urls_and_counts if aggregated_urls_and_counts else [],
        u'start_date': start_date,
        u'end_date': end_date,
        u'package_name': package_name,
        u'all_datasets': dataset_alls,
        u'include_resources': include_resources,
        u'user_name': user_name,
        u'user_all': user_all,
        u'today': today,
        u'error_messages': json.dumps(error_messages),
        u'name_static_tracking': json.dumps(name_static_tracking),
    }
    
    if isinstance(urls_and_counts, dict):
        error_message = urls_and_counts.get('error', None)
        if error_message:
            extra_vars[u'error'] = error_message
        else:
            extra_vars[u'start_time'] = urls_and_counts.get('start_time')
            extra_vars[u'end_time'] = urls_and_counts.get('end_time')
            extra_vars[u'package_name'] = urls_and_counts.get('package_name')
            extra_vars[u'all_package_names'] = urls_and_counts.get('all_package_names')
            extra_vars[u'include_resources'] = urls_and_counts.get('include_resources')
    elif isinstance(urls_and_counts, list):
        extra_vars[u'list_data'] = aggregated_urls_and_counts

    return base.render('user/statistical_tracking.html', extra_vars)



# Đây là chức năng thống kê data theo tổ chức 
def statistical_org():
    organization_name = request.form.get('organization_name') or None
    print(organization_name)
    private = request.form.get('private') or None
    state = request.form.get('state') or None
    include_datasets = request.form.get('include_datasets', 'false').lower() == 'true'
    
    try:
        action = 'statistical_org_get_sum'
        datasets_org = logic.get_action(action)(data_dict={
            'organization_name': organization_name,
            'private': private,
            'state': state,
            'include_datasets': include_datasets
        })  
        
    except logic.NotAuthorized:
        return base.abort(403, toolkit._('Need to be system administrator to administer'))

    organization_list = logic.get_action('organization_list')(
        data_dict={'all_fields': True}
    )
    print("this is organization_list --->",organization_list)
    
    extra_vars: dict[str, Any] = {
        u'datasets_org': json.dumps(datasets_org) if datasets_org else '[]',
        u'organization_list': organization_list,
        u'organization_name': organization_name,
        u'state': state,
        u'private': private,
        u'include_datasets': include_datasets,
    }

    return base.render('user/statistical_org.html', extra_vars)

#Dashboard/statistical/statistical_field    
def statistical_field():
    field_name = request.form.getlist('field_name') or [""] 
    private = request.form.get('private') or None
    state = request.form.get('state') or None
    include_datasets = request.form.get('include_datasets', 'false').lower() == 'true'
 
    try:
        action = 'statistical_field_get_sum'
        datasets_field = logic.get_action(action)(data_dict={
            'field_name': field_name,
            'private': private,
            'state': state,
            'include_datasets': include_datasets
        }) 
        
    except logic.NotAuthorized:
        return base.abort(403, toolkit._('Need to be system administrator to administer'))
    
    group_list = logic.get_action('group_list')(
        data_dict={'all_fields': True}
     )       
    extra_vars: dict[str, Any] = {
        u'datasets_field': json.dumps(datasets_field),
        u'group_list': group_list,
        u'field_name': field_name,
        u'state': state,
        u'private': private,
        u'include_datasets': include_datasets,
    }
    return base.render('user/statistical_field.html', extra_vars)

def statistical_api():
    # Lấy ngày hiện tại và ngày mặc định
    today = datetime.today().date()
    day_default = int(config.get('ckan.day_default'))
    day_tracking_default = today - timedelta(days=day_default)

    # Lấy tham số từ form hoặc sử dụng giá trị mặc định
    start_time = request.form.get('start_time', str(day_tracking_default))
    end_time = request.form.get('end_time', str(today))
    creator_select = request.form.get('creator_select', 'all')
    
    # Lấy tham số từ request args
    limit = int(request.args.get('limit', 100)) 
    page = int(request.args.get('page', 1))  

    # Định nghĩa API URL
    api_url = config.get('ckan.url_api')

    # Tham số gửi đi trong request
    payload = {
        "start_time": start_time,
        "end_time": end_time,
        "creator_select": creator_select,
        "limit": limit,
        "page": page 
    }

    headers = {
        "Content-Type": config.get('ckan.content_type'),
        "Authorization": config.get('ckan.authorization')
    }

    try:
        # Gửi request đến API
        response = requests.get(api_url, json=payload, headers=headers)
        response.raise_for_status()  # Kiểm tra lỗi HTTP

        # Lấy dữ liệu trả về
        data = response.json()
        if data.get("success"):
            static_api = data.get("result", [])
            print("API Result:", static_api)
        else:
            static_api = []
            print("API Error:", data.get("error", "Unknown error"))

    except requests.exceptions.RequestException as e:
        static_api = []
        print("Request Exception:", str(e))
    
    creators = static_api.get("creators", [])
    
    for creator in creators:
        print(f"Value: {creator.get('value')}, Text: {creator.get('text')}")
    error_messages = get_validation_error_messages()
    chart_name_api = get_info_chart_name_api()

    # Tạo extra_vars để truyền sang template
    extra_vars = {
        u'static_api': json.dumps(static_api) if static_api else '[]',
        u'creators': creators,
        u'start_time': start_time,
        u'end_time': end_time,
        u'creator_select': creator_select,
        u'limit': limit,
        u'page': page ,
        u'today': today,
        u'chart_name_api': json.dumps(chart_name_api),
        u'error_messages': json.dumps(error_messages),
    }

    # Trả về trang giao diện với dữ liệu đã lọc
    return base.render('user/statistical_api.html', extra_vars)



#Dashboard/statistical/new_user_stats
def new_user_statistical():
    today = datetime.today().date()
    day_default = int(config.get('ckan.day_default'))
    day_tracking_default = today - timedelta(days=day_default)

    start_date = request.form.get('start_date', str(day_tracking_default))
    end_date = request.form.get('end_date', str(today))
    state = request.form.get('state', 'active')
    date_list = [start_date,end_date]

    try:
        action = 'stats_new_users'
        urls_and_counts = logic.get_action(action)(data_dict={
            u'start_date': start_date,
            u'end_date': end_date,
            u'state': state,
        })

    except logic.NotAuthorized:
        return base.abort(403, toolkit._('Need to be system administrator to administer'))
    print("this is urls_and_counts --->",date_list)
    error_messages = get_validation_error_messages()
    
      
    print("this is urls_and_counts --->",urls_and_counts)
    extra_vars: dict[str, Any] = {
        u'urls_and_counts': json.dumps(urls_and_counts),
        u'state': state, 
        u'count': urls_and_counts['total_user_created_count'],
        u'date_list': date_list,
        u'error_messages': json.dumps(error_messages),
        u'today': today,
        
    }

    return base.render('user/new_user_stats.html', extra_vars)

#Dashboard/statistical/user_login_stats
def user_login_statistical():
    today = datetime.today().date()
    day_default = int(config.get('ckan.day_default'))
    day_tracking_default = today - timedelta(days=day_default)

    start_date = request.form.get('start_date', str(day_tracking_default))
    end_date = request.form.get('end_date', str(today))
    user_name = request.form.get('user_name')
    
    user_name_list = toolkit.get_action('user_list')(data_dict={})
    user_name_list = [user['name'] for user in user_name_list]

    try:
        action = 'login_activity_show'
        data_dict = {
            u'start_date': start_date,
            u'end_date': end_date,
        }
        if user_name:  
            data_dict[u'user_name'] = user_name

        urls_and_counts = logic.get_action(action)(data_dict=data_dict)
    except logic.NotAuthorized:
        return base.abort(403, toolkit._('Need to be system administrator to administer'))
    
    error_messages = get_validation_error_messages()
    
    
    date_list = []
    start_date = datetime.strptime(start_date, '%Y-%m-%d')
    end_date = datetime.strptime(end_date, '%Y-%m-%d')
    current_date = start_date
    while current_date <= end_date:
        date_list.append(current_date.strftime('%Y-%m-%d'))
        current_date += timedelta(days=1)
    
    count = 0
    login_data = {date: 0 for date in date_list} 
    for user in urls_and_counts['login_activity']:
        for login in user['login_history']:
            login_date = login['login_time'].split(' ')[1] 
            if login_date in login_data:
                login_data[login_date] += 1
                count+=1
                
    extra_vars: dict[str, Any] = {
        u'login_data': json.dumps(login_data),
        u'date_list': json.dumps(date_list),
        u'count': count,
        u'user_name_filtered': user_name,
        u'user_name_list': user_name_list,
        u'error_messages': json.dumps(error_messages),
        u'today': today,
        
    }

    return base.render('user/user_login_stats.html', extra_vars)

def json_serial(obj):
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()  # Chuyển thành chuỗi định dạng ISO 8601
    raise TypeError(f"Type {type(obj)} not serializable")

def statistical_datatypes():
    today = datetime.today().date()
    day_default = int(config.get('ckan.day_default'))
    day_tracking_default = today - timedelta(days=day_default)

    start_date = request.form.get('start_date', str(day_tracking_default))
    end_date = request.form.get('end_date', str(today))
    format_type = request.form.get('format_type') or None
    
    try:
        action = 'resource_access_by_date'
        data_types = logic.get_action(action)(data_dict={
            u'start_date': start_date,
            u'end_date': end_date,
            u'format_type': format_type,
        })
    except logic.NotAuthorized:
        return base.abort(403, toolkit._('Need to be system administrator to administer'))
    
    color_chart_format = color_chart_datatypes()
    error_messages = get_validation_error_messages()

    
    list_datatypes = set()
    
    # Gọi package_search để lấy dữ liệu
    results = logic.get_action('package_search')(data_dict={})
    
    # Duyệt qua các dataset
    for package in results.get('results', []):
        for resource in package.get('resources', []):
            format_value = resource.get('format', '').strip().lower()
            if format_value:
                list_datatypes.add(format_value)     
                     
    extra_vars: dict[str, Any] = {
            u'data_types': json.dumps(data_types, default=json_serial),  # Sử dụng hàm `json_serial` để xử lý date
            u'start_date': start_date,
            u'end_date': end_date,
            u'list_datatypes': list_datatypes,
            u'format_type': format_type,
            u'today': today,
            u'color_chart_format': json.dumps(color_chart_format),
            u'error_messages': json.dumps(error_messages),
    }     
    return base.render('user/statistical_datatypes.html', extra_vars)


def statistical_user_time():
    today = datetime.today().date()
    day_default = int(config.get('ckan.day_default'))
    day_tracking_default = today - timedelta(days=day_default)

    start_date = request.form.get('start_date', str(day_tracking_default))
    end_date = request.form.get('end_date', str(today))
    include_user_info_detail = request.form.get('include_user_info_detail') or True
    sys_admin = request.form.get('sys_admin') or None
    
    start_date_obj = datetime.strptime(start_date, '%Y-%m-%d')
    end_date_obj = datetime.strptime(end_date, '%Y-%m-%d')
    days_difference = str((end_date_obj - start_date_obj).days)
    
    try:
        action = 'stats_users'
        list_user_time = logic.get_action(action)(data_dict={
            'recent_active_days': days_difference,
            'target_active_date': end_date,
            'include_user_info_detail': include_user_info_detail,
            'sys_admin': sys_admin,
        })  
        
    except logic.NotAuthorized:
        return base.abort(403, toolkit._('Need to be system administrator to administer'))
    
    
    error_messages = get_validation_error_messages()
    
    extra_vars: dict[str, Any] = {
        u'list_user_time': json.dumps(list_user_time, default=json_serial),
        u'start_date': start_date,
        u'end_date': end_date,
        u'include_user_info_detail': include_user_info_detail,
        u'sys_admin': sys_admin,
        u'error_messages': json.dumps(error_messages),
        u'today': today,
        
    }

    return base.render('user/statistical_user_time.html', extra_vars)

def statistical_resource():
    today = datetime.today().date()
    
    day_default = int(config.get('ckan.day_default'))
    day_tracking_default = today - timedelta(days=day_default)
    start_date = request.form.get('start_date', str(day_tracking_default))
    end_date = request.form.get('end_date', str(today))
    organizations = request.form.get('organizations') or None
    package_name = request.form.get('package_name') or None
    
    try:
        action = 'get_datasets_statistics'
        list_datasets = logic.get_action(action)(data_dict={
            'start_date': start_date,
            'end_date': end_date,
            'organizations': organizations,
            'package_name': package_name,
        })  
        
    except logic.NotAuthorized:
        return base.abort(403, toolkit._('Need to be system administrator to administer'))
    
    dataset_alls = logic.get_action('package_list')(data_dict={'all_fields': True})
    print("this is dataset_alls --->",dataset_alls)
    organization_list = logic.get_action('organization_list')(data_dict={'all_fields': True})
    error_messages = get_validation_error_messages()
    
    
    
    extra_vars: dict[str, Any] = {
        u'list_datasets': json.dumps(list_datasets, default=json_serial),
        u'start_date': start_date,
        u'end_date': end_date,
        u'organizations': organizations,
        u'organization_list': organization_list,
        u'package_name': package_name,
        u'dataset_alls': dataset_alls,
        u'error_messages': json.dumps(error_messages),
        u'today': today,
        
    }
    return base.render('user/statistical_resource.html', extra_vars)



dashboard.add_url_rule(
    u"/statistical/resource-dashboard", view_func=resource_dashboard, methods=['GET']
)
dashboard.add_url_rule(
    u"/statistical/user-dashboard", view_func=user_dashboard, methods=['GET']
)

dashboard.add_url_rule(
    u"/statistical/statistical-tracking", view_func=statistical_tracking, methods=['GET', 'POST']
)

dashboard.add_url_rule(
    u"/statistical/statistical-org", view_func=statistical_org, methods=['GET', 'POST']
)

dashboard.add_url_rule(
    u"/statistical/statistical-field", view_func=statistical_field, methods=['GET', 'POST']
)

dashboard.add_url_rule(
    u"/statistical/statistical-api", view_func=statistical_api, methods=['GET', 'POST']
)

dashboard.add_url_rule(
    u"/statistical", view_func=statistical, methods=['GET', 'POST']
)
dashboard.add_url_rule(
    u"/statistical/user_login_stats", view_func=user_login_statistical, methods=['GET', 'POST']
)
dashboard.add_url_rule(
    u"/statistical/user_login", view_func=user_login_statistical, methods=['GET', 'POST']
)
dashboard.add_url_rule(
    u"/statistical/new_user_stats", view_func=new_user_statistical, methods=['GET', 'POST']
)
dashboard.add_url_rule(
    u"/statistical/user_time_stats", view_func=statistical_user_time, methods=['GET', 'POST']
)

dashboard.add_url_rule(
    u"/statistical/statistical-datatypes", view_func=statistical_datatypes,methods=['GET', 'POST']
)

dashboard.add_url_rule(
    u"/statistical/statistical-resource", view_func=statistical_resource,methods=['GET', 'POST']
)

def get_blueprints():
    return [dashboard]