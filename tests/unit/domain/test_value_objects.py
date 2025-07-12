"""Unit tests for domain value objects."""

import pytest

from src.domain.value_objects.location import Coordinates, NodeLocation
from src.domain.value_objects.measurements import (
    FlowRate,
    Pressure,
    Temperature,
    Volume,
)
from src.domain.value_objects.node_status import NodeStatus
from src.domain.value_objects.quality_metrics import DataQualityMetrics
from src.domain.value_objects.sensor_type import SensorType


class TestMeasurements:
    """Test cases for measurement value objects."""

    def test_temperature_validation(self):
        """Test temperature value validation."""
        # Valid temperatures
        temp1 = Temperature(20.5)
        assert temp1.value == 20.5
        assert temp1.unit == "°C"

        # Edge cases
        temp2 = Temperature(-50.0)
        assert temp2.value == -50.0

        temp3 = Temperature(100.0)
        assert temp3.value == 100.0

        # Invalid temperatures
        with pytest.raises(ValueError):
            Temperature(-51.0)

        with pytest.raises(ValueError):
            Temperature(101.0)

    def test_temperature_conversions(self):
        """Test temperature unit conversions."""
        temp = Temperature(25.0)

        assert temp.to_fahrenheit() == 77.0
        assert temp.to_kelvin() == 298.15

    def test_flow_rate_validation(self):
        """Test flow rate value validation."""
        # Valid flow rates
        flow1 = FlowRate(100.5)
        assert flow1.value == 100.5
        assert flow1.unit == "L/s"

        # Invalid flow rates
        with pytest.raises(ValueError, match="cannot be negative"):
            FlowRate(-1.0)

        with pytest.raises(ValueError, match="exceeds maximum"):
            FlowRate(10001.0)

    def test_flow_rate_conversions(self):
        """Test flow rate unit conversions."""
        flow = FlowRate(100.0)

        assert flow.to_cubic_meters_per_hour() == 360.0
        assert pytest.approx(flow.to_gallons_per_minute(), 0.1) == 1585.0

    def test_pressure_validation(self):
        """Test pressure value validation."""
        # Valid pressures
        pressure1 = Pressure(4.5)
        assert pressure1.value == 4.5
        assert pressure1.unit == "bar"

        # Invalid pressures
        with pytest.raises(ValueError, match="cannot be negative"):
            Pressure(-1.0)

        with pytest.raises(ValueError, match="exceeds maximum"):
            Pressure(21.0)

    def test_volume_validation(self):
        """Test volume value validation."""
        # Valid volumes
        vol1 = Volume(1000.0)
        assert vol1.value == 1000.0
        assert vol1.unit == "m³"

        # Invalid volumes
        with pytest.raises(ValueError, match="cannot be negative"):
            Volume(-1.0)

    def test_measurement_immutability(self):
        """Test that measurements are immutable."""
        temp = Temperature(20.0)

        with pytest.raises(AttributeError):
            temp.value = 25.0

        with pytest.raises(AttributeError):
            temp.unit = "°F"


class TestLocation:
    """Test cases for location value objects."""

    def test_coordinates_validation(self):
        """Test coordinates validation."""
        # Valid coordinates
        coords1 = Coordinates(39.2154, 9.1097)  # Cagliari
        assert coords1.latitude == 39.2154
        assert coords1.longitude == 9.1097

        # Edge cases
        Coordinates(90.0, 180.0)
        Coordinates(-90.0, -180.0)

        # Invalid coordinates
        with pytest.raises(ValueError):
            Coordinates(91.0, 0.0)

        with pytest.raises(ValueError):
            Coordinates(0.0, 181.0)

    def test_node_location_validation(self):
        """Test node location validation."""
        # Valid location
        location = NodeLocation(
            site_name="Selargius",
            area="Cagliari",
            pcr_unit="PCR-123",
            coordinates=Coordinates(39.2154, 9.1097),
        )

        assert location.site_name == "Selargius"
        assert location.area == "Cagliari"
        assert location.pcr_unit == "PCR-123"
        assert location.full_location == "Selargius - Cagliari - PCR: PCR-123"

        # Required fields
        with pytest.raises(ValueError, match="Site name is required"):
            NodeLocation(site_name="", area="Cagliari")

        with pytest.raises(ValueError, match="Area is required"):
            NodeLocation(site_name="Selargius", area="")

    def test_location_to_dict(self):
        """Test location serialization."""
        location = NodeLocation(
            site_name="Selargius",
            area="Cagliari",
            pcr_unit="PCR-123",
            coordinates=Coordinates(39.2154, 9.1097),
            address="Via Roma 123",
        )

        result = location.to_dict()

        assert result["site_name"] == "Selargius"
        assert result["area"] == "Cagliari"
        assert result["pcr_unit"] == "PCR-123"
        assert result["address"] == "Via Roma 123"
        assert result["coordinates"]["latitude"] == 39.2154
        assert result["coordinates"]["longitude"] == 9.1097


class TestQualityMetrics:
    """Test cases for quality metrics value object."""

    def test_quality_metrics_validation(self):
        """Test quality metrics validation."""
        # Valid metrics
        metrics = DataQualityMetrics(
            coverage_percentage=85.5,
            missing_values_count=100,
            anomaly_count=5,
            total_records=1000,
        )

        assert metrics.coverage_percentage == 85.5
        assert metrics.missing_values_count == 100
        assert metrics.anomaly_count == 5
        assert metrics.total_records == 1000

        # Invalid coverage
        with pytest.raises(ValueError):
            DataQualityMetrics(
                coverage_percentage=101.0,
                missing_values_count=0,
                anomaly_count=0,
                total_records=100,
            )

        # Invalid counts
        with pytest.raises(ValueError):
            DataQualityMetrics(
                coverage_percentage=50.0,
                missing_values_count=-1,
                anomaly_count=0,
                total_records=100,
            )

        # Missing values exceed total
        with pytest.raises(ValueError):
            DataQualityMetrics(
                coverage_percentage=50.0,
                missing_values_count=101,
                anomaly_count=0,
                total_records=100,
            )

    def test_quality_score_calculation(self):
        """Test quality score calculation."""
        metrics = DataQualityMetrics(
            coverage_percentage=80.0,
            missing_values_count=50,
            anomaly_count=10,
            total_records=1000,
        )

        # Quality score = 70% coverage + 20% completeness + 10% anomaly-free
        # = 80 * 0.7 + 95 * 0.2 + 99 * 0.1
        # = 56 + 19 + 9.9 = 84.9
        assert metrics.quality_score == 84.9
        assert metrics.is_acceptable is True

    def test_quality_score_edge_cases(self):
        """Test quality score edge cases."""
        # No records
        metrics1 = DataQualityMetrics(
            coverage_percentage=0.0,
            missing_values_count=0,
            anomaly_count=0,
            total_records=0,
        )
        assert metrics1.quality_score == 0.0
        assert metrics1.is_acceptable is False

        # Perfect quality
        metrics2 = DataQualityMetrics(
            coverage_percentage=100.0,
            missing_values_count=0,
            anomaly_count=0,
            total_records=1000,
        )
        assert metrics2.quality_score == 100.0
        assert metrics2.is_acceptable is True


class TestEnumerations:
    """Test cases for enumeration value objects."""

    def test_sensor_type_from_string(self):
        """Test sensor type parsing from string."""
        assert SensorType.from_string("flow") == SensorType.FLOW_METER
        assert SensorType.from_string("FLOW_METER") == SensorType.FLOW_METER
        assert SensorType.from_string("pressure") == SensorType.PRESSURE_SENSOR
        assert SensorType.from_string("temp") == SensorType.TEMPERATURE_SENSOR
        assert SensorType.from_string("multi") == SensorType.MULTI_PARAMETER

        with pytest.raises(ValueError, match="Unknown sensor type"):
            SensorType.from_string("invalid")

    def test_node_status_from_string(self):
        """Test node status parsing from string."""
        assert NodeStatus.from_string("active") == NodeStatus.ACTIVE
        assert NodeStatus.from_string("ACTIVE") == NodeStatus.ACTIVE
        assert NodeStatus.from_string("inactive") == NodeStatus.INACTIVE
        assert NodeStatus.from_string("maintenance") == NodeStatus.MAINTENANCE
        assert NodeStatus.from_string("error") == NodeStatus.ERROR

        with pytest.raises(ValueError, match="Unknown node status"):
            NodeStatus.from_string("invalid")

    def test_node_status_is_operational(self):
        """Test node status operational check."""
        assert NodeStatus.ACTIVE.is_operational() is True
        assert NodeStatus.INACTIVE.is_operational() is False
        assert NodeStatus.MAINTENANCE.is_operational() is False
        assert NodeStatus.ERROR.is_operational() is False
