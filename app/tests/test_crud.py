from app.crud import LinkCRUD
from app.models.constants import SHORT_URL_LENGTH
from app.schemas.links import LinkAddSchema, PaginationParams


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

    async def test_create_short_link_with_custom_code(
            self,
            crud: LinkCRUD,
            sample_url: str
    ):
        """Тест создания новой ссылки с пользовательским коротким кодом."""
        custom_code = "custom"
        sample_schema = LinkAddSchema(url=sample_url, custom_code=custom_code)
        short_link = await crud.create_short_link(sample_schema)
        assert short_link is not None
        assert short_link.short_url == custom_code
        assert str(short_link.original_url) == sample_url

    async def test_create_short_link_with_existing_custom_code(
            self,
            crud: LinkCRUD,
            sample_url: str,
            another_sample_url: str
    ):
        """Тест создания новой ссылки с уже существующим коротким кодом."""
        custom_code = "custom"
        sample_schema_1 = LinkAddSchema(
            url=sample_url, custom_code=custom_code
        )
        await crud.create_short_link(sample_schema_1)
        sample_schema_2 = LinkAddSchema(
            url=another_sample_url, custom_code=custom_code
        )
        try:
            await crud.create_short_link(sample_schema_2)
            assert False, "Ожидалось ValueError при дублировании кода."
        except ValueError as e:
            assert str(e) == "Пользовательский короткий код уже существует."

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

    async def test_get_all_links(
            self,
            crud: LinkCRUD,
            sample_url: str
    ):
        """Тест получения информации обо всех ссылках."""
        # Создаем несколько ссылок для теста
        for i in range(3):
            await crud.create_short_link(
                LinkAddSchema(url=f"{sample_url}/{i}")
            )
        links = await crud.get_all_links(
            pagination=PaginationParams(limit=10, offset=0)
        )
        assert isinstance(links, list)
        assert len(links) == 3
        for link in links:
            assert str(link.original_url).startswith(sample_url)
            assert len(link.short_url) == SHORT_URL_LENGTH
