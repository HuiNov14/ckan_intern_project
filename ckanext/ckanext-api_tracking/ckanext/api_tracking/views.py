import math
from typing import Any
from unittest import result
from flask import Blueprint, request
import ckan.plugins.toolkit as toolkit
from ckan.common import current_user, config
import ckanext.api_tracking.logic.auth as auth  # Thay bằng tên extension thực tế của bạn
from datetime import datetime, timedelta
from ckan import logic
import ckan.lib.base as base
from ckan.lib.helpers import helper_functions as h
from ckan.lib.helpers import Page

# Blueprint for tracking
dashboard = Blueprint('tracking_blueprint', __name__, url_prefix=u'/dashboard')

def aggregate_package_views(urls_and_counts):
    """Aggregate package views for each unique package."""
    aggregated_data = {}
    
    # Loop through the tracking data
    for url in urls_and_counts:
        for tracking in url['tracking']:
            package_name = tracking['package']
            package_views = tracking['package_view']
            title = tracking['title']
            
            # If package is already in the aggregated data, sum the views
            if package_name in aggregated_data:
                aggregated_data[package_name]['package_view'] += package_views
            else:
                aggregated_data[package_name] = {
                    'package': package_name,
                    'package_view': package_views,
                    'title': title
                }
    
    # Convert the aggregated data back to a list for rendering
    return list(aggregated_data.values())

def statistical():
    # Get query parameters
    today = datetime.today().date()     
    day_tracking_default = today - timedelta(days=int(config.get('ckan.day_default')))
    
    # Initialize variables outside the request.method check
    start_date = request.form.get('start_date', str(day_tracking_default))  # Handle the form start_date
    end_date = request.form.get('end_date', str(today))  # Handle the form end_date
    package_name = request.form.getlist('package_name') or [""] # From form data
    include_resources = request.form.get('include_resources') == 'on'  # From form data
    user_name = [name.strip() for name in request.form.get('user_name', '').split(',')]
    is_admin = current_user.sysadmin
    

    # Check access rights
    try:
        logic.check_access('tracking_access', {})
    except logic.NotAuthorized:
        return base.abort(403, toolkit._('Need to be system administrator to administer'))

    # Fetch tracking data based on admin status
    try:
        action = 'tracking_by_user' if is_admin else 'tracking_urls_and_counts'
        urls_and_counts = logic.get_action(action)(data_dict={
            u'user_name': user_name,
            u'start_date': start_date,
            u'end_date': end_date,
            u'package_name': package_name,
            u'include_resources': include_resources,
        })  # type: ignore
        for package in urls_and_counts:
            print('abccccccccccccccccccccc=================>', package)
        

    except logic.ValidationError as e:
        urls_and_counts = []
        

    # Aggregate the package views
    aggregated_urls_and_counts = aggregate_package_views(urls_and_counts)
    
  
    
    # Prepare variables for rendering
    extra_vars: dict[str, Any] = {
        u'urls_and_counts': aggregated_urls_and_counts,
        u'start_date': start_date,
        u'end_date': end_date,
        u'package_name': package_name,
        u'include_resources': include_resources,
        u'user_name': user_name,
        u'is_admin': is_admin,
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
            extra_vars[u'include_resources'] = urls_and_counts.get('include_resources')
    elif isinstance(urls_and_counts, list):
        # Pass aggregated data to template
        extra_vars[u'list_data'] = aggregated_urls_and_counts

    # Render the template with the prepared variables
    return base.render('user/dashboard_statistical.html', extra_vars)

# Register route for blueprint
dashboard.add_url_rule(
    u"/statistical", view_func=statistical, methods=['GET', 'POST']
)

def get_blueprints():
    return [dashboard]