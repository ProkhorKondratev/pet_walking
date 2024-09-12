import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from tortoise.contrib.fastapi import RegisterTortoise

from .routing import orders_router
from .services import OrderService

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler("app.log"), logging.StreamHandler()],
)
logger = logging.getLogger(__name__)
logging.getLogger('watchfiles').setLevel(logging.WARNING)


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with RegisterTortoise(
        app,
        db_url='sqlite://db.sqlite3',
        modules={'models': ['pet_walking.models']},
        generate_schemas=True,
    ):
        logger.info('Приложение запускается')
        await OrderService.add_initial_walkers()
        yield
        logger.info('Приложение завершает работу')


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get('/', include_in_schema=False)
async def redirect_to_docs():
    logger.info('Переадресация на /docs')
    return RedirectResponse(url='/docs')


@app.get('/health', include_in_schema=False)
async def health():
    return {'status': 'ok'}


app.include_router(orders_router)
