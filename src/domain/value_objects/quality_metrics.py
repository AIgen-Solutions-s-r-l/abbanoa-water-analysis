from dataclasses import dataclass
from typing import Any, Dict


@dataclass(frozen=True)
class DataQualityMetrics:
    """Value object representing data quality metrics."""

    coverage_percentage: float
    missing_values_count: int
    anomaly_count: int
    total_records: int

    def __post_init__(self) -> None:
        self._validate()

    def _validate(self) -> None:
        """Validate quality metrics."""
        if not 0 <= self.coverage_percentage <= 100:
            raise ValueError(
                f"Coverage percentage must be between 0 and 100: {self.coverage_percentage}"
            )

        if self.missing_values_count < 0:
            raise ValueError(
                f"Missing values count cannot be negative: {self.missing_values_count}"
            )

        if self.anomaly_count < 0:
            raise ValueError(f"Anomaly count cannot be negative: {self.anomaly_count}")

        if self.total_records < 0:
            raise ValueError(f"Total records cannot be negative: {self.total_records}")

        if self.missing_values_count > self.total_records:
            raise ValueError("Missing values count cannot exceed total records")

    @property
    def quality_score(self) -> float:
        """Calculate overall quality score (0-100)."""
        if self.total_records == 0:
            return 0.0

        # Weight: 70% coverage, 20% completeness, 10% anomaly-free
        completeness = (
            (self.total_records - self.missing_values_count) / self.total_records * 100
        )
        anomaly_free = (
            (self.total_records - self.anomaly_count) / self.total_records * 100
        )

        score = self.coverage_percentage * 0.7 + completeness * 0.2 + anomaly_free * 0.1

        return round(score, 2)

    @property
    def is_acceptable(self) -> bool:
        """Check if data quality meets minimum acceptable threshold."""
        return self.quality_score >= 70.0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "coverage_percentage": self.coverage_percentage,
            "missing_values_count": self.missing_values_count,
            "anomaly_count": self.anomaly_count,
            "total_records": self.total_records,
            "quality_score": self.quality_score,
            "is_acceptable": self.is_acceptable,
        }
