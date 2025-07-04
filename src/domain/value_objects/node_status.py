from enum import Enum


class NodeStatus(Enum):
    """Enumeration of monitoring node statuses."""
    
    ACTIVE = "active"
    INACTIVE = "inactive"
    MAINTENANCE = "maintenance"
    ERROR = "error"
    
    @classmethod
    def from_string(cls, value: str) -> "NodeStatus":
        """Create NodeStatus from string value."""
        value = value.lower().strip()
        
        for status in cls:
            if status.value == value:
                return status
        
        raise ValueError(f"Unknown node status: {value}")
    
    def is_operational(self) -> bool:
        """Check if the status indicates operational state."""
        return self == NodeStatus.ACTIVE