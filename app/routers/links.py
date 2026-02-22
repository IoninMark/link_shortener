import os

from fastapi import APIRouter, HTTPException, status
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends

from crud import LinkCRUD
from database import get_db
from logger import api_logger
from schemas.links import LinkAddSchema, LinkReadSchema


BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")

# Создаем экземпляр роутера.
# prefix="/links" — это пространство имен. Все маршруты в этом файле
# автоматически получат этот префикс.
# tags=["Ссылки"] — нужно для группировки в
# автоматической документации (Swagger UI).
router = APIRouter(
    prefix="/links",
    tags=["Ссылки"]
)


@router.post("/")
async def create_link(
    request: LinkAddSchema,
    db: AsyncSession = Depends(get_db)
) -> LinkReadSchema:
    """Эндпоинт для создания короткой ссылки."""
    api_logger.debug(
        f"Получен запрос на создание короткой ссылки для URL: {request.url}"
    )
    crud = LinkCRUD(db)
    try:
        short_code = await crud.create_short_link(request)
        api_logger.info(
            f"Создана короткая ссылка: {short_code.short_url} "
            f"-> {short_code.original_url}"
        )
        return LinkReadSchema(
            short_url=f"{BASE_URL}/{short_code.short_url}",
            original_url=short_code.original_url
        )
    except ValueError as e:
        api_logger.error(f"Ошибка при создании короткой ссылки: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )


@router.get(
        "/{slug}",
        summary="Редирект по короткой ссылке",
        description="Редирект по короткой ссылке",
    )
async def redirect_to_url(
    slug: str,
    db: AsyncSession = Depends(get_db)
):
    """Эндпоинт для редиректа по оригинальной ссылке."""
    api_logger.debug(
        f"Получен запрос на переход по короткой ссылке: {slug}"
    )
    crud = LinkCRUD(db)
    original_url = await crud.get_original_link(slug)
    if not original_url:
        api_logger.warning(
            f"Короткая ссылка не найдена: {slug}"
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ссылка не найдена."
        )
    api_logger.info(
        f"Редирект по короткой ссылке: {slug} -> {original_url}"
    )
    return RedirectResponse(
        url=original_url,
        status_code=status.HTTP_302_FOUND
    )
