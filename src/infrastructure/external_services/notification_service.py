"""Notification service implementations."""

import logging
from typing import Dict, List, Optional

from src.application.interfaces.notification_service import (
    INotificationService,
    NotificationChannel,
    NotificationPriority,
)


class LoggingNotificationService(INotificationService):
    """Simple notification service that logs notifications."""
    
    def __init__(self) -> None:
        self.logger = logging.getLogger(__name__)
    
    async def send_notification(
        self,
        recipient: str,
        subject: str,
        message: str,
        priority: NotificationPriority = NotificationPriority.MEDIUM,
        channels: Optional[List[NotificationChannel]] = None,
        metadata: Optional[Dict[str, any]] = None
    ) -> None:
        """Log notification details."""
        channels_str = ", ".join([c.value for c in (channels or [NotificationChannel.EMAIL])])
        
        self.logger.info(
            f"NOTIFICATION [{priority.value}] to {recipient} via {channels_str}: "
            f"{subject} - {message}"
        )
        
        if metadata:
            self.logger.debug(f"Metadata: {metadata}")
    
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
        for recipient in recipients:
            await self.send_notification(
                recipient, subject, message, priority, channels, metadata
            )
    
    async def send_anomaly_alert(
        self,
        node_id: str,
        anomaly_type: str,
        severity: str,
        description: str,
        measurement_data: Dict[str, float]
    ) -> None:
        """Send an anomaly detection alert."""
        priority_map = {
            "critical": NotificationPriority.CRITICAL,
            "high": NotificationPriority.HIGH,
            "medium": NotificationPriority.MEDIUM,
            "low": NotificationPriority.LOW
        }
        
        priority = priority_map.get(severity, NotificationPriority.MEDIUM)
        
        subject = f"Anomaly Detected - {anomaly_type} [{severity.upper()}]"
        message = f"Node {node_id}: {description}\nMeasurements: {measurement_data}"
        
        await self.send_notification(
            recipient="system-alerts@water-infrastructure.com",
            subject=subject,
            message=message,
            priority=priority,
            channels=[NotificationChannel.EMAIL, NotificationChannel.SMS],
            metadata={"node_id": node_id, "anomaly_type": anomaly_type}
        )
    
    async def send_threshold_alert(
        self,
        node_id: str,
        measurement_type: str,
        current_value: float,
        threshold_value: float,
        threshold_type: str
    ) -> None:
        """Send a threshold exceeded alert."""
        severity = "high" if abs(current_value - threshold_value) / threshold_value > 0.5 else "medium"
        
        subject = f"Threshold Exceeded - {measurement_type} [{severity.upper()}]"
        message = (
            f"Node {node_id}: {measurement_type} has exceeded {threshold_type} threshold\n"
            f"Current: {current_value}, Threshold: {threshold_value}"
        )
        
        await self.send_notification(
            recipient="system-alerts@water-infrastructure.com",
            subject=subject,
            message=message,
            priority=NotificationPriority.HIGH if severity == "high" else NotificationPriority.MEDIUM,
            channels=[NotificationChannel.EMAIL],
            metadata={
                "node_id": node_id,
                "measurement_type": measurement_type,
                "threshold_type": threshold_type
            }
        )