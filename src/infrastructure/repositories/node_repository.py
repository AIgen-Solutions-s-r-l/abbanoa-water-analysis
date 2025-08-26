
from typing import List
import asyncpg
from src.schemas.node import Node

class NodeRepository:
    def __init__(self, pool: asyncpg.Pool):
        self.pool = pool

    async def get_all_nodes(self) -> List[Node]:
        async with self.pool.acquire() as conn:
            rows = await conn.fetch("""
                SELECT node_id, node_name, node_type, is_active, 
                       latitude, longitude, metadata, created_at
                FROM water_infrastructure.nodes
                WHERE is_active = true
                ORDER BY node_name
            """)
            
            nodes = []
            for row in rows:
                nodes.append(Node(
                    id=row["node_id"],
                    name=row["node_name"],
                    location={
                        "site_name": row["node_name"].split()[0] if row["node_name"] else "Unknown",
                        "area": "Sardinia",
                        "coordinates": {
                            "latitude": float(row["latitude"]) if row["latitude"] else 0,
                            "longitude": float(row["longitude"]) if row["longitude"] else 0
                        }
                    },
                    node_type=row["node_type"],
                    status="active" if row["is_active"] else "inactive",
                    description=f"Monitoring station - {row['node_id']}"
                ))
            
            return nodes
