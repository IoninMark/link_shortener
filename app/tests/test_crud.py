from app.crud import LinkCRUD
from app.models.constants import SHORT_URL_LENGTH
from app.schemas.links import LinkAddSchema


class TestLinkCRUD:
    """Тесты для CRUD операций над ссылками."""

    async def test_create_short_link(
            self,
            crud: LinkCRUD,
            sample_url: str
    ):
        """Тест создания новой ссылки."""
        sample_schema = LinkAddSchema(url=sample_url)
        short_link = await crud.create_short_link(sample_schema)
        assert short_link is not None
        assert len(short_link.short_url) == SHORT_URL_LENGTH
        assert str(short_link.original_url) == sample_url

    async def test_get_original_url(
            self,
            crud: LinkCRUD,
            sample_url: str
    ):
        """Тест получения оригинальной ссылки по короткой."""
        sample_schema = LinkAddSchema(url=sample_url)
        short_link = await crud.create_short_link(sample_schema)
        url = await crud.get_original_link(short_link.short_url)
        assert url == sample_url

    async def test_get_original_url_not_found(
            self,
            crud: LinkCRUD
    ):
        """Тест получения ссылки по несуществующему короткому коду."""
        url = await crud.get_original_link("nonexistent")
        assert url is None
