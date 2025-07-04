"""Use case for detecting anomalies in water network."""

from datetime import datetime, timedelta
from typing import List, Optional
from uuid import UUID

from src.application.dto.analysis_results_dto import AnomalyDetectionResultDTO
from src.application.interfaces.event_bus import IEventBus
from src.application.interfaces.notification_service import (
    INotificationService,
    NotificationPriority
)
from src.application.interfaces.repositories import (
    IMonitoringNodeRepository,
    ISensorReadingRepository
)
from src.domain.services.anomaly_detection_service import AnomalyDetectionService


class DetectNetworkAnomaliesUseCase:
    """Use case for detecting anomalies across the water network."""
    
    def __init__(
        self,
        sensor_reading_repository: ISensorReadingRepository,
        monitoring_node_repository: IMonitoringNodeRepository,
        anomaly_detection_service: AnomalyDetectionService,
        event_bus: IEventBus,
        notification_service: INotificationService
    ) -> None:
        self.sensor_reading_repository = sensor_reading_repository
        self.monitoring_node_repository = monitoring_node_repository
        self.anomaly_detection_service = anomaly_detection_service
        self.event_bus = event_bus
        self.notification_service = notification_service
    
    async def execute(
        self,
        network_id: Optional[UUID] = None,
        node_ids: Optional[List[UUID]] = None,
        time_window_hours: int = 24,
        notify_on_critical: bool = True
    ) -> List[AnomalyDetectionResultDTO]:
        """Detect anomalies in the network for specified nodes or all nodes."""
        # Determine which nodes to analyze
        if node_ids:
            nodes = []
            for node_id in node_ids:
                node = await self.monitoring_node_repository.get_by_id(node_id)
                if node:
                    nodes.append(node)
        else:
            # Get all active nodes
            nodes = await self.monitoring_node_repository.get_all(active_only=True)
        
        if not nodes:
            raise ValueError("No monitoring nodes found for analysis")
        
        # Set time range
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(hours=time_window_hours)
        
        all_anomalies = []
        
        # Analyze each node
        for node in nodes:
            # Get readings for the node
            readings = await self.sensor_reading_repository.get_by_node_id(
                node_id=node.id,
                start_time=start_time,
                end_time=end_time
            )
            
            if len(readings) < 10:  # Skip if insufficient data
                continue
            
            # Detect anomalies
            anomaly_events = self.anomaly_detection_service.detect_anomalies(
                readings=readings,
                reference_time=end_time
            )
            
            # Convert to DTOs and process
            for event in anomaly_events:
                anomaly_dto = AnomalyDetectionResultDTO(
                    node_id=node.id,
                    timestamp=event.occurred_at,
                    anomaly_type=event.anomaly_type,
                    severity=event.severity,
                    measurement_type=event.sensor_type,
                    actual_value=event.measurement_value,
                    expected_range=(
                        event.threshold - (event.threshold * 0.1),
                        event.threshold + (event.threshold * 0.1)
                    ),
                    deviation_percentage=abs(
                        (event.measurement_value - event.threshold) / event.threshold * 100
                    ),
                    description=event.description
                )
                
                all_anomalies.append(anomaly_dto)
                
                # Publish event
                await self.event_bus.publish(event)
                
                # Send notification for critical anomalies
                if notify_on_critical and event.severity in ["critical", "high"]:
                    await self._send_anomaly_notification(node.name, anomaly_dto)
        
        return all_anomalies
    
    async def _send_anomaly_notification(
        self,
        node_name: str,
        anomaly: AnomalyDetectionResultDTO
    ) -> None:
        """Send notification for critical anomalies."""
        priority_map = {
            "critical": NotificationPriority.CRITICAL,
            "high": NotificationPriority.HIGH,
            "medium": NotificationPriority.MEDIUM,
            "low": NotificationPriority.LOW
        }
        
        await self.notification_service.send_anomaly_alert(
            node_id=str(anomaly.node_id),
            anomaly_type=anomaly.anomaly_type,
            severity=anomaly.severity,
            description=f"Anomaly detected at {node_name}: {anomaly.description}",
            measurement_data={
                anomaly.measurement_type: anomaly.actual_value
            }
        )