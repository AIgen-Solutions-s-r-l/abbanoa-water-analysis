
from typing import List, Optional
from src.infrastructure.repositories.reading_repository import ReadingRepository
from src.schemas.reading import Reading

class ReadingService:
    def __init__(self, reading_repository: ReadingRepository):
        self.reading_repository = reading_repository

    async def get_node_readings(self, node_id: str, start_time: Optional[str], end_time: Optional[str], max_points: int) -> List[Reading]:
        return await self.reading_repository.get_node_readings(node_id, start_time, end_time, max_points)
