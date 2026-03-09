import random
import string

from sqlalchemy import select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.links import (
    LinkAddSchema,
    LinkInfoSchema,
    LinkReadSchema,
    PaginationParams
)
from app.logger import db_logger
from app.models.links import LinkModel
from app.models.constants import SHORT_URL_LENGTH


class LinkCRUD:
    """Класс для операций CRUD с ссылками."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def generate_short_code(self, length: int = SHORT_URL_LENGTH) -> str:
        """Функция генерации случайного короткого кода для ссылки."""
        db_logger.debug("Генерация короткого кода для ссылки...")
        while True:
            code = ''.join(random.choices(
                string.ascii_letters + string.digits, k=length
            ))
            result = await self.db.execute(
                select(LinkModel).where(LinkModel.short_url == code)
            )
            if not result.scalar_one_or_none():
                db_logger.debug(f"Сгенерирован короткий код: {code}")
                return code

    async def create_short_link(
            self, original_url: LinkAddSchema
    ) -> LinkReadSchema:
        """Создание короткой ссылки."""
        db_logger.debug(
            f"Создание короткой ссылки для URL: {original_url.url}"
        )
        short_code = await self.generate_short_code()
        new_link = LinkModel(
            short_url=short_code,
            original_url=str(original_url.url)
        )
        self.db.add(new_link)
        try:
            await self.db.commit()
            await self.db.refresh(new_link)
            db_logger.info(
                f"Короткая ссылка успешно сохранена в базе данных: "
                f"{new_link.short_url} -> {new_link.original_url}"
            )
            return LinkReadSchema.model_validate(new_link)
        except IntegrityError:
            db_logger.error(
                "Ошибка при сохранении ссылки в базу данных. "
                "Возможно, короткий код уже существует."
            )
            await self.db.rollback()
            raise ValueError("Ошибка при сохранении ссылки в базу данных.")

    async def get_original_link(self, short_code: str) -> str | None:
        """Получение оригинальной ссылки по короткому коду."""
        db_logger.debug(
            f"Получение оригинальной ссылки для короткого кода: {short_code}"
        )
        result = await self.db.execute(
            select(LinkModel).where(LinkModel.short_url == short_code)
        )
        link = result.scalar_one_or_none()
        if link:
            # Увеличиваем счетчик переходов по ссылке
            await self.db.execute(
                update(LinkModel).where(
                    LinkModel.short_url == short_code
                ).values(clicks=LinkModel.clicks + 1)
            )
            await self.db.commit()
            db_logger.info(
                f"Оригинальная ссылка найдена для кода {short_code}: "
                f"{link.original_url}"
            )
            return str(link.original_url)
        db_logger.warning(
            f"Оригинальная ссылка не найдена для кода: {short_code}"
        )
        return None

    async def get_link_info(self, short_code: str) -> LinkInfoSchema | None:
        """Получение информации о ссылке по короткому коду."""
        db_logger.debug(
            f"Получение информации о ссылке для короткого кода: {short_code}"
        )
        result = await self.db.execute(
            select(LinkModel).where(LinkModel.short_url == short_code)
        )
        link = result.scalar_one_or_none()
        if link:
            db_logger.info(
                f"Информация о ссылке найдена для кода {short_code}: "
                f"{link.original_url}"
            )
            return LinkInfoSchema.model_validate(link)
        db_logger.warning(
            f"Информация о ссылке не найдена для кода: {short_code}"
        )
        return None

    async def get_all_links(
            self,
            pagination: PaginationParams) -> list[LinkInfoSchema]:
        """Получение информации обо всех ссылках."""
        db_logger.debug("Получение информации обо всех ссылках...")
        result = await self.db.execute(
            select(LinkModel)
            .order_by(LinkModel.created_at.desc())
            .limit(pagination.limit)
            .offset(pagination.offset)
        )
        links = result.scalars().all()
        db_logger.info(f"Найдено {len(links)} ссылок в базе данных.")
        return [LinkInfoSchema.model_validate(link) for link in links]
