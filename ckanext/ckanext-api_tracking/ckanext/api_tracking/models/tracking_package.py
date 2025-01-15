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
from ..helpers import check_download, check_dataset, check_resource

log = logging.getLogger(__name__)

__all__ = ["TrackingPackagesInfo"]

# Global variable to hold the tracking packages table
tracking_packages_table = None


def init_db():
    """Initialize the tracking_packages_table if it doesn't exist."""
    global tracking_packages_table

    # Define the table schema
    define_tables()

    # Check if the table exists in the database
    engine = model.meta.engine
    # if engine.has_table('tracking_packages_table'):
    #     tracking_packages_table.drop(engine)
    #     log.info("Dropped existing table: tracking_packages_table")
    if not engine.has_table('tracking_packages_table'):
        # Create the table if it doesn't exist
        tracking_packages_table.create(engine)
        log.info("Table created: tracking_packages_table")
    else:
        log.info("Table already exists: tracking_packages_table")


def define_tables():
    """Define the schema for the tracking packages table."""
    global tracking_packages_table

    tracking_packages_table = sa.Table(
        'tracking_packages_table',
        model.meta.metadata,
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('url', sa.UnicodeText, nullable=False),
        sa.Column('user_key', sa.UnicodeText, nullable=False),
        sa.Column('package_id', sa.UnicodeText, nullable=False),
        sa.Column('resource_id', sa.UnicodeText, nullable=False),
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
        id: Optional[int] = None,
        url: str = "",
        user_key: str = "",
        package_id: str = "",
        resource_id: str = "",
        tracking_type: str = "",
        count: int = 0,
        running_total: int = 0,
        recent_views: int = 0,
        tracking_date: Optional[datetime.datetime] = None
    ) -> None:
        super().__init__()
        self.id = id
        self.url = url
        self.user_key = user_key
        self.package_id = package_id
        self.resource_id = resource_id
        self.tracking_type = tracking_type
        self.count = count
        self.running_total = running_total
        self.recent_views = recent_views
        self.tracking_date = tracking_date

def normalize_url(url: str) -> str:
    """Chuẩn hóa URL bằng cách loại bỏ http/https, query params và trailing slash."""
    import re
    url = re.sub(r'^https?://', '', url)  # Bỏ giao thức
    url = re.sub(r'[\?\#].*$', '', url)   # Bỏ query params và fragment
    url = url.rstrip('/')                 # Bỏ dấu / ở cuối
    return url.lower()    

def update_tracking_info() -> None:
    """Update tracking information by aggregating URLs from tracking_raw, only URLs starting with /dataset/."""
    session = meta.Session()

    try:
        # Query to get unique URLs starting with /dataset/ and count them per day
        results = session.execute(
            sa.text("""
                SELECT 
                    url,
                    user_key,
                    tracking_type,
                    DATE(access_timestamp) AS tracking_date,
                    COUNT(*) AS count
                FROM tracking_raw
                GROUP BY url, user_key, tracking_type, DATE(access_timestamp)
            """)
        )

        for row in results:
            url = row["url"]
            user_key = row["user_key"]
            tracking_type = row["tracking_type"]
            tracking_date = row["tracking_date"]
            count = row["count"]

            # Validate URL with check functions
            if not (check_dataset(url) or check_resource(url) or check_download(url)):
                log.info(f"URL skipped: {url}")
                continue

            # Extract package name from the URL
            if url.startswith("/dataset/") and "/" not in url[len("/dataset/"):]:
                package_name = url.split("/dataset/")[1]
            else:
                package_name = None

            # Query the package table to get the corresponding package_id
            package_id = session.execute(
                sa.text("""
                    SELECT id FROM package
                    WHERE name = :package_name
                """),
                {"package_name": package_name}
            ).scalar()

            # If package_id is not found, set it to a default value
            package_id = package_id if package_id else '~~not~found~~'
            
            normalized_url = normalize_url(url)
            # Extract resource_id from the URL
            if "/dataset/" in normalized_url and "/resource/" in normalized_url:
                try:
                    resource_id = normalized_url.split("/resource/")[1].split("/")[0]
                except IndexError:
                    resource_id = None
            else:
                resource_id = None
                
            if resource_id:
                valid_resource = session.execute(
                    sa.text("SELECT id FROM resource WHERE id = :resource_id"), 
                    {"resource_id": resource_id}
                ).scalar()

                if not valid_resource:
                    log.warning(f"Resource ID không tồn tại: {resource_id}")
                    resource_id = None

            running_total = session.execute(
                sa.text("""
                    SELECT SUM(count) 
                    FROM tracking_packages_table
                    WHERE url = :url AND user_key = :user_key
                    AND tracking_date <= :tracking_date
                """),
                {"url": url, "user_key": user_key, "tracking_date": tracking_date}
            ).scalar() or 0

            # Calculate recent_views (total count in the last 14 days for this url and user_key)
            recent_views = session.execute(
                sa.text("""
                    SELECT SUM(count) 
                    FROM tracking_packages_table
                    WHERE url = :url AND user_key = :user_key
                    AND tracking_date BETWEEN :start_date AND :tracking_date
                """),
                {
                    "url": url,
                    "user_key": user_key,
                    "start_date": tracking_date - datetime.timedelta(days=14),
                    "tracking_date": tracking_date
                }
            ).scalar() or 0

            # Check if a record already exists for this URL and date
            tracking_record = (
                session.query(TrackingPackagesInfo)
                .filter_by(url=url, tracking_date=tracking_date, user_key=user_key, tracking_type=tracking_type)
                .first()
            )

            if tracking_record:
                # Update the existing record
                tracking_record.count = count
                tracking_record.package_id = package_id
                tracking_record.running_total = running_total
                tracking_record.recent_views = recent_views
                log.info(f"Updated tracking info for URL: {url} on {tracking_date}")
            else:
                # Insert a new record
                new_tracking_info = TrackingPackagesInfo(
                    url=url,
                    user_key=user_key,
                    package_id=package_id,
                    resource_id=resource_id or "~~not found~~",
                    tracking_type=tracking_type,
                    count=count,
                    running_total=running_total,
                    recent_views=recent_views,
                    tracking_date=tracking_date,
                )
                session.add(new_tracking_info)
                log.info(f"Inserted new tracking info for URL: {url} on {tracking_date}")

        # Commit the session
        session.commit()
    except Exception as e:
        log.error(f"Error updating tracking info: {e}")
        session.rollback()
    finally:
        session.close()


