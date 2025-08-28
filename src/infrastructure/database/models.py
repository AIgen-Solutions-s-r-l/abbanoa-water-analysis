"""
SQLAlchemy models for the water infrastructure database.
"""

from datetime import datetime
from typing import Optional
from sqlalchemy import Column, String, Float, DateTime, Boolean, Integer, Text, JSON
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Node(Base):
    """Node model representing infrastructure nodes."""
    __tablename__ = 'nodes'
    __table_args__ = {'schema': 'water_infrastructure'}

    node_id = Column(String(50), primary_key=True)
    node_name = Column(String(100), nullable=False)
    node_type = Column(String(50), nullable=False)
    location_name = Column(String(100))
    latitude = Column(Float)
    longitude = Column(Float)
    installation_date = Column(DateTime)
    last_maintenance_date = Column(DateTime)
    is_active = Column(Boolean, default=True)
    node_metadata = Column(JSON)  # Using JSON instead of JSONB for compatibility
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class SensorReading(Base):
    """Sensor reading model representing time-series data."""
    __tablename__ = 'sensor_readings'
    __table_args__ = {'schema': 'water_infrastructure'}

    timestamp = Column(DateTime, primary_key=True)
    node_id = Column(String(50), primary_key=True)
    temperature = Column(Float)
    flow_rate = Column(Float)
    pressure = Column(Float)
    total_flow = Column(Float)
    quality_score = Column(Float)
    is_interpolated = Column(Boolean, default=False)
    raw_data = Column(JSON)  # Using JSON instead of JSONB for compatibility


class Anomaly(Base):
    """Anomaly model representing detected anomalies."""
    __tablename__ = 'anomalies'
    __table_args__ = {'schema': 'water_infrastructure'}

    anomaly_id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, nullable=False)
    node_id = Column(String(50), nullable=False)
    anomaly_type = Column(String(50), nullable=False)
    severity = Column(String(20), nullable=False)
    measurement_type = Column(String(50))
    actual_value = Column(Float)
    expected_value = Column(Float)
    deviation_percentage = Column(Float)
    detection_method = Column(String(50))
    is_confirmed = Column(Boolean, default=False)
    resolved_at = Column(DateTime)
    anomaly_metadata = Column(JSON)  # Using JSON instead of JSONB for compatibility
    created_at = Column(DateTime, default=datetime.utcnow)
