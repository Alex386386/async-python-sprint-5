from http import HTTPStatus

from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.sql import func

from app.api.routers import main_router
from app.core.config import settings
from app.core.db import get_async_session
from app.core.init_db import create_first_superuser

app = FastAPI(title=settings.app_title)

app.include_router(main_router)


@app.on_event('startup')
async def startup():
    await create_first_superuser()


@app.get(
    '/ping',
    tags=['ping'],
    description='Проверить подключение к базе данных.',
)
async def ping_db(session: AsyncSession = Depends(get_async_session)):
    try:
        result = await session.execute(select(func.now()))
        current_time = result.scalar_one_or_none()
        if current_time:
            return {'status': 'ok', 'timestamp': current_time}
        raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                            detail='Database error')
    except Exception as e:
        raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                            detail=str(e))
