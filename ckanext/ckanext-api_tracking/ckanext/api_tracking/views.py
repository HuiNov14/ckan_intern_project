import json
from typing import Any
from flask import Blueprint, request
import ckan.plugins.toolkit as toolkit
from ckan.common import config
import ckanext.api_tracking.logic.auth as auth  # Thay bằng tên extension thực tế của bạn
from datetime import datetime, timedelta
from ckan import logic
import ckan.lib.base as base
from ckan.lib.helpers import helper_functions as h
from ckan.lib.helpers import Page

# Blueprint for tracking
dashboard = Blueprint('tracking_blueprint', __name__, url_prefix=u'/dashboard/')

#Function aggregate package
def aggregate_package_views(urls_and_counts):
    """Aggregate package views for each unique package."""
    aggregated_data = {}
    
    # Loop through the tracking data
    for url in urls_and_counts: 
        user_name = url['user_name']
        for tracking in url['tracking']:
            package_name = tracking['package']
            package_id = tracking['package_id']
            package_views = tracking['package_view']
            title = tracking['title']
            include_resources = tracking.get('include_resources', [])
            print("include_resources===================>",include_resources)
            if not package_id:
                continue
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
                }
    
    # Convert the aggregated data back to a list for rendering
    return list(aggregated_data.values())

#Dashboard/statistical
def statistical():

    try:
        logic.check_access('user_check', {})
    except logic.NotAuthorized:
        return base.abort(403, toolkit._('Need to be system administrator to administer'))

    return base.render('user/dashboard_statistical.html')

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
        logic.check_access('user_check', {})
    except logic.NotAuthorized:
        return base.abort(403, toolkit._('Need to be system administrator to administer'))
 
    try:
        action = 'tracking_by_user'
        urls_and_counts = logic.get_action(action)(data_dict={
            u'user_name': user_name,
            u'start_date': start_date,
            u'end_date': end_date,
            u'package_name': package_name,
            u'include_resources': True,
        }) 

    except logic.ValidationError as e:
        urls_and_counts = []
        
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

##Dashboard/statistical/statistical_org
def statistical_org():
    organization_name = request.form.get('organization_name') or 'organization-yqra-9121-gaar'
    print(organization_name)
    private = request.form.get('private') or None
    state = request.form.get('state') or None
    include_datasets = request.form.get('include_datasets', 'false').lower() == 'true'
    try:
        logic.check_access('user_check', {})
    except logic.NotAuthorized:
        return base.abort(403, toolkit._('Need to be system administrator to administer'))
 
    try:
        action = 'statistical_org_get_sum'
        datasets_org = logic.get_action(action)(data_dict={
            'organization_name': organization_name,
            'private': private,
            'state': state,
            'include_datasets': include_datasets
        })  
        
    except logic.ValidationError as e:
        datasets_org = []
 
    print("========================>",datasets_org)
    organization_list = logic.get_action('organization_list')(data_dict={})
 
    extra_vars: dict[str, Any] = {
        u'datasets_org': json.dumps(datasets_org),
        u'organization_list': organization_list,
        u'organization_name': organization_name,
        u'state': state,
        u'private': private,
        u'include_datasets': include_datasets,
    }
    if isinstance(datasets_org, dict):
        error_message = datasets_org.get('error', None)
        if error_message:
            extra_vars[u'error'] = error_message
        else:
            extra_vars[u'id_org'] = datasets_org.get('id_org')
            extra_vars[u'private'] = datasets_org.get('private')
            extra_vars[u'state'] = datasets_org.get('state')
            extra_vars[u'include_datasets'] = datasets_org.get('include_datasets')
    return base.render('user/statistical_org.html', extra_vars)

#Dashboard/statistical/statistical_field    
def statistical_field():
    field_name = request.form.getlist('field_name') or [""] 
    private = request.form.get('private') or None
    state = request.form.get('state') or None
    include_datasets = request.form.get('include_datasets', 'false').lower() == 'true'
    try:
        logic.check_access('user_check', {})
    except logic.NotAuthorized:
        return base.abort(403, toolkit._('Need to be system administrator to administer'))
 
    try:
        action = 'statistical_field_get_sum'
        datasets_field = logic.get_action(action)(data_dict={
            'field_name': field_name,
            'private': private,
            'state': state,
            'include_datasets': include_datasets
        }) 
        
    except logic.ValidationError as e:
        datasets_field = []
        
        print('field name =====>',field_name)
 
    tag_list = logic.get_action('tag_list')(data_dict={})
 
    extra_vars: dict[str, Any] = {
        u'datasets_field': json.dumps(datasets_field),
        u'tag_list': tag_list,
        u'field_name': field_name,
        u'state': state,
        u'private': private,
        u'include_datasets': include_datasets,
    }
    if isinstance(datasets_field, dict):
        error_message = datasets_field.get('error', None)
        if error_message:
            extra_vars[u'error'] = error_message
        else:
            extra_vars[u'id_field'] = datasets_field.get('id_field')
            extra_vars[u'private'] = datasets_field.get('private')
            extra_vars[u'state'] = datasets_field.get('state')
            extra_vars[u'include_datasets'] = datasets_field.get('include_datasets')
    return base.render('user/statistical_field.html', extra_vars)

#Dashboard/statistical/new_user_stats
def new_user_statistical():

    try:
        logic.check_access('user_check', {})
    except logic.NotAuthorized:
        return base.abort(403, toolkit._('Need to be system administrator to administer'))

    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    state = request.args.get('state', 'active')
    date_list = [start_date,end_date]

    try:
        action = 'stats_new_users'
        urls_and_counts = logic.get_action(action)(data_dict={
            u'start_date': start_date,
            u'end_date': end_date,
            u'state': state,
        })

    except Exception as e:
        raise toolkit.ValidationError(f"api request error: {e}")    
    
    extra_vars: dict[str, Any] = {
        u'urls_and_counts': urls_and_counts,
        u'state': state, 
        u'count': urls_and_counts['total_user_created_count'],
        u'date_list': date_list,
    }

    return base.render('user/new_user_stats.html', extra_vars)

#Dashboard/statistical/user_login_stats
def user_login_statistical():

    try:
        logic.check_access('user_check', {})
    except logic.NotAuthorized:
        return base.abort(403, toolkit._('Need to be system administrator to administer'))
    start_date = request.args.get('start_date', "2024-11-20")
    end_date = request.args.get('end_date', datetime.now().strftime('%Y-%m-%d'))
    user_name = request.args.get('user_name')
    state = request.args.get('state', 'active')
    
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
    except Exception as e:
        raise toolkit.ValidationError(f"api request error: {e}")  
    
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
        u'date_list': date_list,
        u'login_data': login_data,
        u'count': count,
        u'user_name': user_name,
        u'user_name_list': user_name_list
    }

    return base.render('user/user_login_stats.html', extra_vars)

# Register route tracking for blueprint
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
    u"/statistical", view_func=statistical, methods=['GET', 'POST']
)
dashboard.add_url_rule(
    u"/statistical/user_login_stats", view_func=user_login_statistical, methods=['GET', 'POST']
)
dashboard.add_url_rule(
    u"/statistical/new_user_stats", view_func=new_user_statistical, methods=['GET', 'POST']
)

def get_blueprints():
    return [dashboard]