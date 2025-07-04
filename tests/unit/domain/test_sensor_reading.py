"""Unit tests for SensorReading entity."""

from datetime import datetime
from uuid import UUID, uuid4

import pytest

from src.domain.entities.sensor_reading import SensorReading
from src.domain.value_objects.measurements import (
    FlowRate,
    Pressure,
    Temperature,
    Volume,
)
from src.domain.value_objects.sensor_type import SensorType


class TestSensorReading:
    """Test cases for SensorReading entity."""

    def test_create_sensor_reading_with_all_measurements(self):
        """Test creating a sensor reading with all measurement types."""
        node_id = uuid4()
        timestamp = datetime.now()

        reading = SensorReading(
            node_id=node_id,
            sensor_type=SensorType.MULTI_PARAMETER,
            timestamp=timestamp,
            temperature=Temperature(22.5),
            flow_rate=FlowRate(125.3),
            pressure=Pressure(4.2),
            volume=Volume(1234.5),
        )

        assert reading.node_id == node_id
        assert reading.sensor_type == SensorType.MULTI_PARAMETER
        assert reading.timestamp == timestamp
        assert reading.temperature.value == 22.5
        assert reading.flow_rate.value == 125.3
        assert reading.pressure.value == 4.2
        assert reading.volume.value == 1234.5

    def test_create_sensor_reading_with_partial_measurements(self):
        """Test creating a sensor reading with only some measurements."""
        node_id = uuid4()
        timestamp = datetime.now()

        reading = SensorReading(
            node_id=node_id,
            sensor_type=SensorType.FLOW_METER,
            timestamp=timestamp,
            flow_rate=FlowRate(100.0),
            volume=Volume(1000.0),
        )

        assert reading.flow_rate.value == 100.0
        assert reading.volume.value == 1000.0
        assert reading.temperature is None
        assert reading.pressure is None

    def test_sensor_reading_requires_at_least_one_measurement(self):
        """Test that sensor reading requires at least one measurement."""
        with pytest.raises(
            ValueError, match="At least one measurement must be provided"
        ):
            SensorReading(
                node_id=uuid4(),
                sensor_type=SensorType.MULTI_PARAMETER,
                timestamp=datetime.now(),
            )

    def test_sensor_reading_requires_node_id(self):
        """Test that sensor reading requires a node ID."""
        with pytest.raises(ValueError, match="Node ID is required"):
            SensorReading(
                node_id=None,
                sensor_type=SensorType.FLOW_METER,
                timestamp=datetime.now(),
                flow_rate=FlowRate(100.0),
            )

    def test_sensor_reading_requires_timestamp(self):
        """Test that sensor reading requires a timestamp."""
        with pytest.raises(ValueError, match="Timestamp is required"):
            SensorReading(
                node_id=uuid4(),
                sensor_type=SensorType.FLOW_METER,
                timestamp=None,
                flow_rate=FlowRate(100.0),
            )

    def test_sensor_reading_to_dict(self):
        """Test converting sensor reading to dictionary."""
        node_id = uuid4()
        reading_id = uuid4()
        timestamp = datetime.now()

        reading = SensorReading(
            id=reading_id,
            node_id=node_id,
            sensor_type=SensorType.MULTI_PARAMETER,
            timestamp=timestamp,
            temperature=Temperature(20.0),
            flow_rate=FlowRate(150.0),
        )

        result = reading.to_dict()

        assert result["id"] == str(reading_id)
        assert result["node_id"] == str(node_id)
        assert result["sensor_type"] == "multi_parameter"
        assert result["timestamp"] == timestamp.isoformat()
        assert result["temperature"]["value"] == 20.0
        assert result["temperature"]["unit"] == "°C"
        assert result["flow_rate"]["value"] == 150.0
        assert result["flow_rate"]["unit"] == "L/s"
        assert "pressure" not in result
        assert "volume" not in result

    def test_sensor_reading_equality(self):
        """Test sensor reading equality based on ID."""
        id1 = uuid4()
        id2 = uuid4()
        node_id = uuid4()
        timestamp = datetime.now()

        reading1 = SensorReading(
            id=id1,
            node_id=node_id,
            sensor_type=SensorType.FLOW_METER,
            timestamp=timestamp,
            flow_rate=FlowRate(100.0),
        )

        reading2 = SensorReading(
            id=id1,  # Same ID
            node_id=node_id,
            sensor_type=SensorType.FLOW_METER,
            timestamp=timestamp,
            flow_rate=FlowRate(200.0),  # Different value
        )

        reading3 = SensorReading(
            id=id2,  # Different ID
            node_id=node_id,
            sensor_type=SensorType.FLOW_METER,
            timestamp=timestamp,
            flow_rate=FlowRate(100.0),
        )

        assert reading1 == reading2  # Same ID
        assert reading1 != reading3  # Different ID
        assert hash(reading1) == hash(reading2)
        assert hash(reading1) != hash(reading3)
