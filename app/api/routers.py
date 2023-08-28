from fastapi import APIRouter

from app.api.endpoints import downloaded_file_router, user_router

main_router = APIRouter()
main_router.include_router(
    downloaded_file_router,
    prefix='/files',
    tags=['Files']
)
main_router.include_router(user_router)
