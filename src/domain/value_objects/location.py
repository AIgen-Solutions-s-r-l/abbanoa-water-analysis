from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass(frozen=True)
class Coordinates:
    """Value object representing geographical coordinates."""

    latitude: float
    longitude: float

    def __post_init__(self) -> None:
        self._validate()

    def _validate(self) -> None:
        """Validate coordinate values."""
        if not -90 <= self.latitude <= 90:
            raise ValueError(
                f"Latitude {self.latitude} is out of valid range (-90 to 90)"
            )

        if not -180 <= self.longitude <= 180:
            raise ValueError(
                f"Longitude {self.longitude} is out of valid range (-180 to 180)"
            )

    def to_dict(self) -> Dict[str, float]:
        """Convert coordinates to dictionary."""
        return {"latitude": self.latitude, "longitude": self.longitude}


@dataclass(frozen=True)
class NodeLocation:
    """Value object representing a monitoring node location."""

    site_name: str
    area: str
    pcr_unit: Optional[str] = None
    coordinates: Optional[Coordinates] = None
    address: Optional[str] = None

    def __post_init__(self) -> None:
        self._validate()

    def _validate(self) -> None:
        """Validate location data."""
        if not self.site_name or not self.site_name.strip():
            raise ValueError("Site name is required")

        if not self.area or not self.area.strip():
            raise ValueError("Area is required")

    @property
    def full_location(self) -> str:
        """Get full location string."""
        parts = [self.site_name, self.area]
        if self.pcr_unit:
            parts.append(f"PCR: {self.pcr_unit}")
        return " - ".join(parts)

    def to_dict(self) -> Dict[str, Any]:
        """Convert location to dictionary."""
        data = {
            "site_name": self.site_name,
            "area": self.area,
            "pcr_unit": self.pcr_unit,
            "address": self.address,
        }

        if self.coordinates:
            data["coordinates"] = self.coordinates.to_dict()

        return data
