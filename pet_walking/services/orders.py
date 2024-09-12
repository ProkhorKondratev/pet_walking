import logging
from datetime import datetime

from tortoise.functions import Coalesce
from fastapi import HTTPException

from pet_walking.models import WalkOrderModel, WalkerModel
from pet_walking.schemas import WalkOrderCreate, WalkOrder

logger = logging.getLogger(__name__)


class OrderService:
    async def create_order(self, order: WalkOrderCreate) -> WalkOrder:
        """Создает заказ на прогулку собаки."""
        if order.walk_time.minute not in [0, 30]:
            logger.warning(f'Некорректное время начала прогулки (0 или 30 минут): {order.walk_time}')
            raise HTTPException(status_code=400, detail='Прогулка может начинаться только в начале или в половину часа')

        if order.walk_time.hour < 7 or order.walk_time.hour > 22:
            logger.warning(f'Некорректное время начала прогулки (Не между 7 и 23 часами): {order.walk_time}')
            raise HTTPException(status_code=400, detail='Часы выгула собак: с 7 утра до 23 вечера')

        busy_walkers = await WalkOrderModel.filter(walk_time=order.walk_time).values_list('walker_id', flat=True)

        available_walker = await WalkerModel.exclude(id__in=busy_walkers).first()

        if not available_walker:
            logger.warning(f'Все сотрудники заняты на {order.walk_time}')
            raise HTTPException(status_code=400, detail='Все сотрудники заняты')

        new_order = await WalkOrderModel.create(
            walker=available_walker,
            apartment_number=order.apartment_number,
            pet_name=order.pet_name,
            pet_breed=order.pet_breed,
            walk_time=order.walk_time,
        )
        new_order.walker_name = available_walker.name
        logger.info(f'Создан заказ на прогулку: {new_order.id}')

        return WalkOrder.model_validate(new_order)

    async def get_orders(self, date: datetime | None = None) -> list[WalkOrder]:
        """Возвращает список заказов на прогулку собак."""
        orders = WalkOrderModel.annotate(walker_name=Coalesce('walker__name', 'Неизвестно')).prefetch_related('walker')
        if date:
            logger.info(f'Получение заказов на {date}')
            orders = orders.filter(walk_time=date)

        return [WalkOrder.model_validate(order) async for order in orders]

    @staticmethod
    async def add_initial_walkers(initial_walkers: list[str] = ["Петр", "Антон"]) -> None:
        """Добавляет стартовых выгуливающих в базу данных, если их нет."""
        for walker_name in initial_walkers:
            walker_exists = await WalkerModel.filter(name=walker_name).exists()
            if not walker_exists:
                await WalkerModel.create(name=walker_name)
                logger.info(f'Добавлен новый сотрудник: {walker_name}')
