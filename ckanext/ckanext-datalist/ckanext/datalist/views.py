import math
from typing import Any
from flask import Blueprint, request
import ckan.plugins.toolkit as toolkit
import ckanext.api_tracking.logic.auth as auth 
from datetime import datetime, timedelta
from ckan import logic
import ckan.lib.base as base

dashboard = Blueprint('tracking_blueprint', __name__, url_prefix=u'/dashboard')

#Dashboard/statistical
def statistical():

    try:
        logic.check_access('user_check', {})
    except logic.NotAuthorized:
        return base.abort(403, toolkit._('Need to be system administrator to administer'))

    return base.render('user/dashboard_statistical.html')

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