import datetime
from sqlalchemy import func, literal
import ckan.model as model
import ckan.model.meta as meta
from ckan.plugins.toolkit import ValidationError

class ExtendedResourceTable(model.Resource):

    @classmethod
    def get_resources_statistics(cls, data_dict):
        
        # Xử lý ngày bắt đầu và kết thúc
        if data_dict.get('start_date'):
            start_date = data_dict['start_date']
        else:
            current_date = datetime.datetime.now().strftime('%Y-%m-%d')
            start_date = current_date
    
        if data_dict.get('end_date'):
            end_date = data_dict['end_date'] + datetime.timedelta(days=1)
        else:
            current_date = datetime.datetime.now().strftime('%Y-%m-%d')
            end_date = datetime.datetime.strptime(current_date, '%Y-%m-%d') + datetime.timedelta(days=1)
        
        try:
            # Xây dựng truy vấn cơ bản với bộ lọc ngày
            query = meta.Session.query(
                cls.name.label('resource_name'), 
                cls.id.label('resource_id'), 
                cls.format,
                func.date(cls.created).label('created_date'), 
                model.Package.name.label('package_name'), 
                model.Group.name.label('organization'),
                (literal('/dataset/') + model.Package.id + literal('/resource/') + cls.id + literal('/download/') + cls.url).label('download_url'),
            ).join(model.Package, cls.package_id == model.Package.id
            ).join(model.Group, model.Package.owner_org == model.Group.id
            ).filter(func.date(cls.created) >= start_date, func.date(cls.created) < end_date)

            # Xử lý filter Organization
            organizations = data_dict.get('organizations')
            if organizations is not None:
                if isinstance(organizations, str):
                    organizations = [organizations]
                if organizations:
                    query = query.filter(model.Group.name.in_(organizations))

            # Xử lý filter Package Name
            package_name = data_dict.get('package_name')
            if package_name is not None:
                if isinstance(package_name, str):
                    package_name = [package_name]
                if package_name:
                    query = query.filter(model.Package.name.in_(package_name))

            # Truy vấn tổng số tài nguyên với các bộ lọc đã áp dụng
            total_resources_query = meta.Session.query(func.count(cls.id)).join(model.Package, cls.package_id == model.Package.id).join(model.Group, model.Package.owner_org == model.Group.id).filter(func.date(cls.created) >= start_date, func.date(cls.created) < end_date)

            if organizations:
                total_resources_query = total_resources_query.filter(model.Group.name.in_(organizations))
            if package_name:
                total_resources_query = total_resources_query.filter(model.Package.name.in_(package_name))

            # Tính tổng số tài nguyên
            total_resources = total_resources_query.scalar()

            # Lấy kết quả tài nguyên sau khi đã áp dụng limit và offset
            result = query.all()

            # Chuyển đổi kết quả từ Row thành dictionary có thể JSON serializable
            result_dict = []
            for row in result:
                result_dict.append({
                    'resource_name': row.resource_name,
                    'resource_id': row.resource_id,
                    'format': row.format,
                    'created_date': row.created_date,
                    'package_name': row.package_name,
                    'organization': row.organization,
                    'download_url': row.download_url
                })
            
        except Exception as e:
            raise ValidationError(f"database query error: {e}")
        
        # Trả về cả tổng số tài nguyên và kết quả tài nguyên sau khi lọc
        return {
            'total_resources': total_resources,  # Tổng số resource sau khi lọc
            'result': result_dict,  # Danh sách các resource sau khi lọc (dưới dạng dictionary)
        }
