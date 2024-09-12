from fastapi.routing import APIRouter
from fastapi import Depends
from datetime import datetime
from pet_walking.schemas import WalkOrder, WalkOrderCreate
from pet_walking.services import OrderService

router = APIRouter()


@router.get("/orders/", response_model=list[WalkOrder])
async def get_orders(date: datetime | None = None, service: OrderService = Depends()):
    return await service.get_orders(date)


@router.post("/orders/", response_model=WalkOrder)
async def create_order(order: WalkOrderCreate, service: OrderService = Depends()):
    return await service.create_order(order)
