
from typing import List
from src.infrastructure.repositories.node_repository import NodeRepository
from src.schemas.node import Node

class NodeService:
    def __init__(self, node_repository: NodeRepository):
        self.node_repository = node_repository

    async def get_all_nodes(self) -> List[Node]:
        return await self.node_repository.get_all_nodes()
