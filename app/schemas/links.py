from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, HttpUrl


class LinkAddSchema(BaseModel):
    """Схема запроса создания новой ссылки."""
    url: HttpUrl = Field(
        description="Оригинальная URL-ссылка для сокращения."
    )

    model_config = ConfigDict(from_attributes=True)


class LinkReadSchema(BaseModel):
    """Схема ответа при получении короткой ссылке."""
    short_url: str = Field(
        description="Сокращенная URL-ссылка."
    )
    original_url: HttpUrl = Field(
        description="Оригинальная URL-ссылка."
    )

    model_config = ConfigDict(from_attributes=True)


class LinkInfoSchema(BaseModel):
    """Схема ответа при получении информации о ссылке."""
    short_url: str = Field(
        description="Сокращенная URL-ссылка."
    )
    original_url: HttpUrl = Field(
        description="Оригинальная URL-ссылка."
    )
    created_at: datetime = Field(
        description="Дата создания"
    )
    clicks: int = Field(
        0,
        description="количество переходов"
    )

    model_config = ConfigDict(from_attributes=True)


class PaginationParams(BaseModel):
    """Схема для пагинации при получении списка ссылок."""
    limit: int = Field(
        10,
        ge=1,
        le=100,
        description="Количество элементов на странице (от 1 до 100)."
    )
    offset: int = Field(
        0,
        ge=0,
        description="Смещение (количество элементов для пропуска)."
    )
