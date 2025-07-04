"""Notification service interface for alerts and notifications."""

from abc import ABC, abstractmethod
from enum import Enum
from typing import Dict, List, Optional


class NotificationPriority(Enum):
    """Notification priority levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class NotificationChannel(Enum):
    """Available notification channels."""
    EMAIL = "email"
    SMS = "sms"
    WEBHOOK = "webhook"
    IN_APP = "in_app"


class INotificationService(ABC):
    """Interface for sending notifications and alerts."""
    
    @abstractmethod
    async def send_notification(
        self,
        recipient: str,
        subject: str,
        message: str,
        priority: NotificationPriority = NotificationPriority.MEDIUM,
        channels: Optional[List[NotificationChannel]] = None,
        metadata: Optional[Dict[str, any]] = None
    ) -> None:
        """Send a notification to a recipient."""
        pass
    
    @abstractmethod
    async def send_batch_notifications(
        self,
        recipients: List[str],
        subject: str,
        message: str,
        priority: NotificationPriority = NotificationPriority.MEDIUM,
        channels: Optional[List[NotificationChannel]] = None,
        metadata: Optional[Dict[str, any]] = None
    ) -> None:
        """Send notifications to multiple recipients."""
        pass
    
    @abstractmethod
    async def send_anomaly_alert(
        self,
        node_id: str,
        anomaly_type: str,
        severity: str,
        description: str,
        measurement_data: Dict[str, float]
    ) -> None:
        """Send an anomaly detection alert."""
        pass
    
    @abstractmethod
    async def send_threshold_alert(
        self,
        node_id: str,
        measurement_type: str,
        current_value: float,
        threshold_value: float,
        threshold_type: str
    ) -> None:
        """Send a threshold exceeded alert."""
        pass