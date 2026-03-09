import os
from typing import Annotated

from fastapi import APIRouter, HTTPException, status
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends

from app.crud import LinkCRUD
from app.database import get_db
from app.logger import api_logger
from app.schemas.links import (
    LinkAddSchema,
    LinkInfoSchema,
    LinkReadSchema,
    PaginationParams
)


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

PaginationDep = Annotated[PaginationParams, Depends(PaginationParams)]


@router.post(
        "/",
        summary="Создание короткой ссылки",
        description="Создание короткой ссылки",
)
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
        return short_code
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
        response_class=RedirectResponse,
        responses={
            status.HTTP_302_FOUND: {
                "description": "Успешный редирект на оригинальный URL."
            },
            status.HTTP_404_NOT_FOUND: {
                "description": "Короткая ссылка не найдена."
            }
        }
    )
async def redirect_to_url(
    slug: str,
    db: AsyncSession = Depends(get_db)
):
    """Эндпоинт для редиректа по короткой ссылке."""
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


@router.get(
        "/{slug}/info",
        summary="Получение информации о ссылке",
        description="Получение информации о ссылке",
        response_model=LinkInfoSchema,
        responses={
            status.HTTP_404_NOT_FOUND: {
                "description": "Короткая ссылка не найдена."
            }
        }
    )
async def get_link_info(
    slug: str,
    db: AsyncSession = Depends(get_db)
):
    """Эндпоинт для получения информации о ссылке."""
    api_logger.debug(
        f"Получен запрос на получение информации о короткой ссылке: {slug}"
    )
    crud = LinkCRUD(db)
    link_info = await crud.get_link_info(slug)
    if not link_info:
        api_logger.warning(
            f"Короткая ссылка не найдена для получения информации: {slug}"
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ссылка не найдена."
        )
    api_logger.info(
        f"Информация о ссылке получена для кода {slug}: "
        f"{link_info.original_url}, кликов: {link_info.clicks}"
    )
    return link_info


@router.get(
        "/",
        summary="Получение информации обо всех ссылках",
        description="Получение информации обо всех ссылках",
        response_model=list[LinkInfoSchema]
    )
async def get_all_links(
    pagination: PaginationDep,
    db: AsyncSession = Depends(get_db),
):
    """Эндпоинт для получения информации обо всех ссылках."""
    api_logger.debug("Получен запрос на получение всех ссылок.")
    crud = LinkCRUD(db)
    links = await crud.get_all_links(pagination=pagination)
    api_logger.info(
        f"Информация обо всех ссылках получена. Количество: {len(links)}"
    )
    return links
