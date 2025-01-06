import json
from flask import Blueprint, request
import ckan.plugins.toolkit as toolkit
from datetime import datetime, timedelta
from ckan import logic
import ckan.lib.base as base

# Blueprint for view
dataset = Blueprint(
    u'dataset', 
    __name__,   
    url_prefix=u'/dataset',
    url_defaults={u'package_type': u'dataset'}
)

def package():
    # Kiểm tra quyền truy cập nếu cần
    # try:
    #     logic.check_access('user_check', {})  
    # except logic.NotAuthorized:
    #     return base.abort(403, toolkit._('Need to be system administrator to administer'))

    return base.render('package/search.html')

dataset.add_url_rule(
    u"/", view_func=package, methods=['GET', 'POST']
)

def get_blueprints():
    return [dataset]
