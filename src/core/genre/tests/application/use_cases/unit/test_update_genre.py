import uuid
from unittest.mock import create_autospec

import pytest

from src.core.category.domain.category import Category
from src.core.category.domain.category_repository import CategoryRepository
from src.core.genre.application.use_cases.update_genre import UpdateGenre
from src.core.genre.application.use_cases.exceptions import GenreNotFound, InvalidGenre, RelatedCategoriesNotFound
from src.core.genre.domain.genre import Genre
from src.core.genre.domain.genre_repository import GenreRepository


@pytest.fixture
def mock_genre_repository() -> GenreRepository:
    return create_autospec(GenreRepository)


@pytest.fixture
def movie_category() -> Category:
    return Category(name="Movie")


@pytest.fixture
def documentary_category() -> Category:
    return Category(name="Documentary")


@pytest.fixture
def mock_category_repository_with_categories(movie_category, documentary_category) -> CategoryRepository:
    repository = create_autospec(CategoryRepository)
    repository.list.return_value = [movie_category, documentary_category]
    return repository


@pytest.fixture
def mock_empty_category_repository() -> CategoryRepository:
    repository = create_autospec(CategoryRepository)
    repository.list.return_value = []
    return repository


@pytest.fixture
def existing_genre() -> Genre:
    return Genre(
        name="Action",
        is_active=True,
        categories={uuid.uuid4(), uuid.uuid4(), uuid.uuid4()}
    )


class TestUpdateGenre:
    def test_when_genre_does_not_exist_then_raise_genre_not_found(
        self,
        mock_genre_repository,
        mock_category_repository_with_categories,
    ):
        # Arrange
        use_case = UpdateGenre(
            repository=mock_genre_repository,
            category_repository=mock_category_repository_with_categories,
        )
        mock_genre_repository.get_by_id.return_value = None
        genre_id = uuid.uuid4()

        # Act & Assert
        with pytest.raises(GenreNotFound, match=f"Genre with {genre_id} not found"):
            use_case.execute(UpdateGenre.Input(
                id=genre_id,
                name="Updated Genre",
                is_active=True,
                categories=set(),
            ))

    def test_when_provided_categories_do_not_exist_then_raise_related_categories_not_found(
        self,
        mock_genre_repository,
        mock_empty_category_repository,
        existing_genre,
    ):
        # Arrange
        use_case = UpdateGenre(
            repository=mock_genre_repository,
            category_repository=mock_empty_category_repository,
        )
        mock_genre_repository.get_by_id.return_value = existing_genre
        category_id = uuid.uuid4()

        # Act & Assert
        with pytest.raises(RelatedCategoriesNotFound, match="Categories with provided IDs not found: ") as exc:
            use_case.execute(UpdateGenre.Input(
                id=existing_genre.id,
                name="Updated Genre",
                is_active=True,
                categories={category_id},
            ))

        assert str(category_id) in str(exc.value)

    def test_when_updated_genre_is_invalid_then_raise_invalid_genre(
        self,
        mock_genre_repository,
        mock_category_repository_with_categories,
        existing_genre,
    ):
        # Arrange
        use_case = UpdateGenre(
            repository=mock_genre_repository,
            category_repository=mock_category_repository_with_categories,
        )
        mock_genre_repository.get_by_id.return_value = existing_genre

        # Act & Assert
        with pytest.raises(InvalidGenre, match="name cannot be empty"):
            use_case.execute(UpdateGenre.Input(
                id=existing_genre.id,
                name="",
                is_active=True,
                categories=set(),
            ))

    def test_when_updated_genre_is_valid_and_categories_exist_then_update_genre(
        self,
        mock_genre_repository,
        mock_category_repository_with_categories,
        existing_genre,
        movie_category,
        documentary_category,
    ):
        # Arrange
        use_case = UpdateGenre(
            repository=mock_genre_repository,
            category_repository=mock_category_repository_with_categories,
        )
        mock_genre_repository.get_by_id.return_value = existing_genre
        new_categories = {movie_category.id, documentary_category.id}

        # Act
        use_case.execute(UpdateGenre.Input(
            id=existing_genre.id,
            name="Updated Genre",
            is_active=False,
            categories=new_categories,
        ))

        # Assert
        mock_genre_repository.update.assert_called_once()
        updated_genre = mock_genre_repository.update.call_args[0][0]
        assert updated_genre.id == existing_genre.id
        assert updated_genre.name == "Updated Genre"
        assert updated_genre.is_active is False
        assert updated_genre.categories == new_categories