
from fastapi import APIRouter, Depends, HTTPException
from typing import List
from src.application.services.node_service import NodeService
from src.schemas.node import Node
from src.presentation.api.dependencies import get_node_service

router = APIRouter()

@router.get("/nodes", response_model=List[Node])
async def list_nodes(node_service: NodeService = Depends(get_node_service)):
    try:
        return await node_service.get_all_nodes()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
