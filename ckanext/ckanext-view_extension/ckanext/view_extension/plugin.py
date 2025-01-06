import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
import ckanext.api_tracking.views as views
import ckan.model as model

class ViewExtensionPlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.IBlueprint)
    plugins.implements(plugins.ITemplateHelpers)
    
    def get_blueprint(self):
        return views.get_blueprints()
    
    def update_config(self, config):
        toolkit.add_template_directory(config, 'templates')
        toolkit.add_public_directory(config, 'public')
        
    def get_helpers(self):
        return {
            'get_org_name_by_id': get_org_name_by_id,
            'get_org_type_by_id': get_org_type_by_id,
            'get_org_img_url_by_id': get_org_img_url_by_id,
            'get_org_tag_by_id': get_org_tag_by_id,
        }

def get_org_name_by_id(org_id):
    org = model.Session.query(model.Group).filter_by(id=org_id, is_organization=True).first()
    if org:
        return org.title  
    return None

def get_org_type_by_id(org_id):
    org = model.Session.query(model.Group).filter_by(id=org_id, is_organization=True).first()
    if org:
        return org.type
    return None

def get_org_img_url_by_id(org_id):
    org = model.Session.query(model.Group).filter_by(id=org_id, is_organization=True).first()
    if org:
        return org.image_url
    return None

def get_org_tag_by_id(org_id):
    tag = (
        model.Session.query(model.Tag)
        .join(model.Package_tag, model.Tag.id == model.Package_tag.tag_id)
        .join(model.Package, model.Package.id == model.Package_tag.package_id)
        .filter(model.Package.owner_org == org_id)
        .first()
    )
    if tag:
        return tag.name
    return None