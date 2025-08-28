"""
Isolated test for SQLAlchemy models.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import pytest
from datetime import datetime
from sqlalchemy import create_engine, Column, String, Float, DateTime, Boolean, Integer, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Create simplified models for testing
Base = declarative_base()


class TestNode(Base):
    """Simplified Node model for testing."""
    __tablename__ = 'nodes'

    node_id = Column(String(50), primary_key=True)
    node_name = Column(String(100), nullable=False)
    node_type = Column(String(50), nullable=False)
    location_name = Column(String(100))
    latitude = Column(Float)
    longitude = Column(Float)
    is_active = Column(Boolean, default=True)
    node_metadata = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)


class TestSensorReading(Base):
    """Simplified SensorReading model for testing."""
    __tablename__ = 'sensor_readings'

    timestamp = Column(DateTime, primary_key=True)
    node_id = Column(String(50), primary_key=True)
    temperature = Column(Float)
    flow_rate = Column(Float)
    pressure = Column(Float)
    total_flow = Column(Float)
    quality_score = Column(Float)
    is_interpolated = Column(Boolean, default=False)
    raw_data = Column(JSON)


class TestNodeModel:
    """Test Node model functionality."""
    
    @pytest.fixture
    def engine(self):
        """Create in-memory SQLite engine for testing."""
        return create_engine("sqlite:///:memory:")
    
    @pytest.fixture
    def session(self, engine):
        """Create database session."""
        Base.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
        return Session()
    
    def test_node_creation(self, session):
        """Test creating a node with required fields."""
        # Arrange
        node = TestNode(
            node_id="DIST01",
            node_name="DIST01",
            node_type="distribution"
        )
        
        # Act
        session.add(node)
        session.commit()
        
        # Assert
        saved_node = session.query(TestNode).filter_by(node_id="DIST01").first()
        assert saved_node is not None
        assert saved_node.node_name == "DIST01"
        assert saved_node.node_type == "distribution"
        assert saved_node.is_active is True
    
    def test_node_with_optional_fields(self, session):
        """Test creating a node with optional fields."""
        # Arrange
        node = TestNode(
            node_id="INTERCON01",
            node_name="INTERCON01",
            node_type="interconnection",
            location_name="Cesena",
            latitude=44.1380,
            longitude=12.2350
        )
        
        # Act
        session.add(node)
        session.commit()
        
        # Assert
        saved_node = session.query(TestNode).filter_by(node_id="INTERCON01").first()
        assert saved_node.location_name == "Cesena"
        assert saved_node.latitude == 44.1380
        assert saved_node.longitude == 12.2350


class TestSensorReadingModel:
    """Test SensorReading model functionality."""
    
    @pytest.fixture
    def engine(self):
        """Create in-memory SQLite engine for testing."""
        return create_engine("sqlite:///:memory:")
    
    @pytest.fixture
    def session(self, engine):
        """Create database session."""
        Base.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
        return Session()
    
    def test_sensor_reading_creation(self, session):
        """Test creating a sensor reading with required fields."""
        # Arrange
        timestamp = datetime.now()
        reading = TestSensorReading(
            timestamp=timestamp,
            node_id="DIST01",
            flow_rate=150.5,
            pressure=3.2
        )
        
        # Act
        session.add(reading)
        session.commit()
        
        # Assert
        saved_reading = session.query(TestSensorReading).filter_by(
            timestamp=timestamp, node_id="DIST01"
        ).first()
        assert saved_reading is not None
        assert saved_reading.flow_rate == 150.5
        assert saved_reading.pressure == 3.2
        assert saved_reading.is_interpolated is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
