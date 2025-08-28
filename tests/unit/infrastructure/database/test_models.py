"""
Unit tests for SQLAlchemy models.
"""

import pytest
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.infrastructure.database.models import Base, Node, SensorReading, Anomaly


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
        node = Node(
            node_id="DIST01",
            node_name="DIST01",
            node_type="distribution"
        )
        
        # Act
        session.add(node)
        session.commit()
        
        # Assert
        saved_node = session.query(Node).filter_by(node_id="DIST01").first()
        assert saved_node is not None
        assert saved_node.node_name == "DIST01"
        assert saved_node.node_type == "distribution"
        assert saved_node.is_active is True
    
    def test_node_with_optional_fields(self, session):
        """Test creating a node with optional fields."""
        # Arrange
        node = Node(
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
        saved_node = session.query(Node).filter_by(node_id="INTERCON01").first()
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
        reading = SensorReading(
            timestamp=timestamp,
            node_id="DIST01",
            flow_rate=150.5,
            pressure=3.2
        )
        
        # Act
        session.add(reading)
        session.commit()
        
        # Assert
        saved_reading = session.query(SensorReading).filter_by(
            timestamp=timestamp, node_id="DIST01"
        ).first()
        assert saved_reading is not None
        assert saved_reading.flow_rate == 150.5
        assert saved_reading.pressure == 3.2
        assert saved_reading.is_interpolated is False
    
    def test_sensor_reading_with_optional_fields(self, session):
        """Test creating a sensor reading with optional fields."""
        # Arrange
        timestamp = datetime.now()
        reading = SensorReading(
            timestamp=timestamp,
            node_id="ZONE01",
            flow_rate=200.0,
            pressure=3.5,
            temperature=22.5,
            total_flow=3600.0,
            quality_score=0.95,
            is_interpolated=True
        )
        
        # Act
        session.add(reading)
        session.commit()
        
        # Assert
        saved_reading = session.query(SensorReading).filter_by(
            timestamp=timestamp, node_id="ZONE01"
        ).first()
        assert saved_reading.temperature == 22.5
        assert saved_reading.total_flow == 3600.0
        assert saved_reading.quality_score == 0.95
        assert saved_reading.is_interpolated is True


class TestAnomalyModel:
    """Test Anomaly model functionality."""
    
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
    
    def test_anomaly_creation(self, session):
        """Test creating an anomaly with required fields."""
        # Arrange
        timestamp = datetime.now()
        anomaly = Anomaly(
            timestamp=timestamp,
            node_id="DIST01",
            anomaly_type="excessive_consumption",
            severity="high"
        )
        
        # Act
        session.add(anomaly)
        session.commit()
        
        # Assert
        saved_anomaly = session.query(Anomaly).filter_by(
            timestamp=timestamp, node_id="DIST01"
        ).first()
        assert saved_anomaly is not None
        assert saved_anomaly.anomaly_type == "excessive_consumption"
        assert saved_anomaly.severity == "high"
        assert saved_anomaly.is_confirmed is False
    
    def test_anomaly_with_optional_fields(self, session):
        """Test creating an anomaly with optional fields."""
        # Arrange
        timestamp = datetime.now()
        anomaly = Anomaly(
            timestamp=timestamp,
            node_id="INTERCON01",
            anomaly_type="pressure_drop",
            severity="medium",
            measurement_type="pressure",
            actual_value=1.5,
            expected_value=3.0,
            deviation_percentage=50.0,
            detection_method="statistical"
        )
        
        # Act
        session.add(anomaly)
        session.commit()
        
        # Assert
        saved_anomaly = session.query(Anomaly).filter_by(
            timestamp=timestamp, node_id="INTERCON01"
        ).first()
        assert saved_anomaly.measurement_type == "pressure"
        assert saved_anomaly.actual_value == 1.5
        assert saved_anomaly.expected_value == 3.0
        assert saved_anomaly.deviation_percentage == 50.0
        assert saved_anomaly.detection_method == "statistical"
