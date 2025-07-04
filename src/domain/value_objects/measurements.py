from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict


@dataclass(frozen=True)
class Measurement(ABC):
    """Base class for all measurement value objects."""

    value: float
    unit: str

    def __post_init__(self) -> None:
        self._validate()

    @abstractmethod
    def _validate(self) -> None:
        """Validate the measurement value."""
        pass

    def to_dict(self) -> Dict[str, Any]:
        """Convert measurement to dictionary."""
        return {"value": self.value, "unit": self.unit}


@dataclass(frozen=True)
class Temperature(Measurement):
    """Value object representing temperature measurement."""

    value: float
    unit: str = "°C"

    def _validate(self) -> None:
        """Validate temperature value."""
        # Reasonable temperature range for water infrastructure
        if not -50 <= self.value <= 100:
            raise ValueError(
                f"Temperature {self.value} is out of valid range (-50 to 100°C)"
            )

    def to_fahrenheit(self) -> float:
        """Convert Celsius to Fahrenheit."""
        return (self.value * 9 / 5) + 32

    def to_kelvin(self) -> float:
        """Convert Celsius to Kelvin."""
        return self.value + 273.15


@dataclass(frozen=True)
class FlowRate(Measurement):
    """Value object representing flow rate measurement."""

    value: float
    unit: str = "L/s"

    def _validate(self) -> None:
        """Validate flow rate value."""
        if self.value < 0:
            raise ValueError(f"Flow rate cannot be negative: {self.value}")

        # Maximum reasonable flow rate (10,000 L/s)
        if self.value > 10000:
            raise ValueError(f"Flow rate {self.value} exceeds maximum reasonable value")

    def to_cubic_meters_per_hour(self) -> float:
        """Convert L/s to m³/h."""
        return self.value * 3.6

    def to_gallons_per_minute(self) -> float:
        """Convert L/s to gallons per minute."""
        return self.value * 15.850323141


@dataclass(frozen=True)
class Pressure(Measurement):
    """Value object representing pressure measurement."""

    value: float
    unit: str = "bar"

    def _validate(self) -> None:
        """Validate pressure value."""
        if self.value < 0:
            raise ValueError(f"Pressure cannot be negative: {self.value}")

        # Maximum reasonable pressure (20 bar)
        if self.value > 20:
            raise ValueError(f"Pressure {self.value} exceeds maximum reasonable value")

    def to_psi(self) -> float:
        """Convert bar to PSI."""
        return self.value * 14.5038

    def to_pascal(self) -> float:
        """Convert bar to Pascal."""
        return self.value * 100000


@dataclass(frozen=True)
class Volume(Measurement):
    """Value object representing volume measurement."""

    value: float
    unit: str = "m³"

    def _validate(self) -> None:
        """Validate volume value."""
        if self.value < 0:
            raise ValueError(f"Volume cannot be negative: {self.value}")

    def to_liters(self) -> float:
        """Convert m³ to liters."""
        return self.value * 1000

    def to_gallons(self) -> float:
        """Convert m³ to gallons."""
        return self.value * 264.172
