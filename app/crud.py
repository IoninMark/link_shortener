import random
import string

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from schemas.links import LinkAddSchema, LinkReadSchema
from logger import db_logger
from models.links import LinkModel
from models.constants import SHORT_URL_LENGTH


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
                db_logger.debug(f"Сгенерирован уникальный короткий код: {code}")
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
            db_logger.info(
                f"Оригинальная ссылка найдена для кода {short_code}: "
                f"{link.original_url}"
            )
            return link.original_url
        db_logger.warning(
            f"Оригинальная ссылка не найдена для кода: {short_code}"
        )
        return None
