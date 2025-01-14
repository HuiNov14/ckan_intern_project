# encoding: utf-8
from __future__ import annotations
import datetime
import logging
from typing import Optional, Any, Dict

import sqlalchemy as sa
from sqlalchemy.orm import mapper

import ckan.model.meta as meta
import ckan.model as model
import ckan.model.domain_object as domain_object
import ckan.model.core as core

log = logging.getLogger(__name__)

__all__ = ["TrackingPackagesInfo"]

# Global variable to hold the tracking packages table
tracking_packages_table = None

def init_db():
    """Initialize the database by defining and creating the tracking packages table if it doesn't exist."""
    global tracking_packages_table

    if tracking_packages_table is None:
        define_tables()

    if not tracking_packages_table.exists():
        tracking_packages_table.create()

def define_tables():
    """Define the schema for the tracking packages table."""
    global tracking_packages_table

    tracking_packages_table = sa.Table(
        'tracking_packages_table',
        model.meta.metadata,
        sa.Column('url', sa.UnicodeText, primary_key=True, nullable=False),
        sa.Column('user_key', sa.UnicodeText, nullable=False),
        sa.Column('package_id', sa.UnicodeText, nullable=False),
        sa.Column('tracking_type', sa.Unicode(10), nullable=False),
        sa.Column('count', sa.Integer, nullable=False),
        sa.Column('running_total', sa.Integer, nullable=False),
        sa.Column('recent_views', sa.Integer, nullable=False),
        sa.Column('tracking_date', sa.DateTime),
    )
    mapper(TrackingPackagesInfo, tracking_packages_table)

class TrackingPackagesInfo(core.StatefulObjectMixin, domain_object.DomainObject):
    """Domain object representing a row in the tracking packages table."""

    def __init__(
        self,
        url: str,
        user_key: str,
        package_id: str,
        tracking_type: str,
        count: int,
        running_total: int,
        recent_views: int,
        tracking_date: datetime.datetime
    ) -> None:
        super().__init__()
        self.url = url
        self.user_key = user_key
        self.package_id = package_id
        self.tracking_type = tracking_type
        self.count = count
        self.running_total = running_total
        self.recent_views = recent_views
        self.tracking_date = tracking_date

    @classmethod
    def get_for_package(cls, package_id: str) -> Dict[str, int]:
        """Get tracking information for a specific package."""
        obj = meta.Session.query(cls).autoflush(False).filter_by(package_id=package_id)
        data = obj.order_by(sa.text('tracking_date desc')).first()

        if data:
            return {
                'total': data.running_total,
                'recent': data.recent_views
            }

        return {'total': 0, 'recent': 0}

    @classmethod
    def get_for_resource(cls, url: str) -> Dict[str, int]:
        """Get tracking information for a specific resource (URL)."""
        obj = meta.Session.query(cls).autoflush(False).filter_by(url=url)
        data = obj.order_by(sa.text('tracking_date desc')).first()

        if data:
            return {
                'total': data.running_total,
                'recent': data.recent_views
            }
        return {'total': 0, 'recent': 0}
    
def update_tracking_info(url: str,user_key: str, package_id: str, tracking_type: str, count: int, running_total: int, recent_views: int, tracking_date: datetime.datetime) -> None:
    """Cập nhật thông tin tracking cho một package cụ thể."""
    # Truy vấn bản ghi cần cập nhật
    query = tracking_packages_table.select().where(
        sa.and_(
            tracking_packages_table.c.url == url,
            tracking_packages_table.c.package_id == package_id
        )
    )
    
    # Kiểm tra nếu bản ghi tồn tại
    result = meta.Session.execute(query).fetchone()
    
    if result:
        # Bản ghi đã tồn tại, tiến hành cập nhật
        update_query = tracking_packages_table.update().where(
            sa.and_(
                tracking_packages_table.c.url == url,
                tracking_packages_table.c.package_id == package_id
            )
        ).values(
            count=count,
            running_total=running_total,
            recent_views=recent_views,
            tracking_date=tracking_date
        )
        meta.Session.execute(update_query)
        meta.Session.commit()
        log.info(f"Đã cập nhật thông tin tracking cho package_id: {package_id}, url: {url}")
    else:
        # Nếu không tìm thấy bản ghi, có thể tạo mới (hoặc thông báo lỗi nếu cần thiết)
        insert_query = tracking_packages_table.insert().values(
            url=url,
            user_key=user_key,  # Bạn có thể thêm giá trị mặc định hoặc thông báo lỗi nếu không có `user_key`
            package_id=package_id,
            tracking_type=tracking_type,  # Tương tự, cần thêm giá trị hợp lý cho `tracking_type`
            count=count,
            running_total=running_total,
            recent_views=recent_views,
            tracking_date=tracking_date
        )
        meta.Session.execute(insert_query)
        meta.Session.commit()
        log.info(f"Đã tạo mới thông tin tracking cho package_id: {package_id}, url: {url}")