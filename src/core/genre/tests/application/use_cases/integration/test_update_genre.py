import uuid

import pytest

from src.core.category.domain.category import Category
from src.core.category.infra.in_memory_category_repository import InMemoryCategoryRepository
from src.core.genre.application.use_cases.update_genre import UpdateGenre
from src.core.genre.application.use_cases.exceptions import GenreNotFound, RelatedCategoriesNotFound
from src.core.genre.domain.genre import Genre
from src.core.genre.infra.in_memory_genre_repository import InMemoryGenreRepository


class TestUpdateGenre:
    def test_when_genre_does_not_exist_then_raise_genre_not_found(self):
        # Arrange
        category_repository = InMemoryCategoryRepository()
        genre_repository = InMemoryGenreRepository()
        
        use_case = UpdateGenre(
            repository=genre_repository,
            category_repository=category_repository,
        )
        genre_id = uuid.uuid4()
        
        # Act & Assert
        with pytest.raises(GenreNotFound, match=f"Genre with {genre_id} not found"):
            use_case.execute(UpdateGenre.Input(
                id=genre_id,
                name="Updated Genre",
                is_active=True,
                categories=set(),
            ))
    
    def test_when_provided_categories_do_not_exist_then_raise_related_categories_not_found(self):
        # Arrange
        category_repository = InMemoryCategoryRepository()
        genre_repository = InMemoryGenreRepository()
        
        # Create a genre
        genre = Genre(name="Action")
        genre_repository.save(genre)
        
        use_case = UpdateGenre(
            repository=genre_repository,
            category_repository=category_repository,
        )
        category_id = uuid.uuid4()
        
        # Act & Assert
        with pytest.raises(RelatedCategoriesNotFound, match="Categories with provided IDs not found: "):
            use_case.execute(UpdateGenre.Input(
                id=genre.id,
                name="Updated Genre",
                is_active=True,
                categories={category_id},
            ))
    
    def test_update_genre_with_valid_data_and_existing_categories(self):
        # Arrange
        category_repository = InMemoryCategoryRepository()
        genre_repository = InMemoryGenreRepository()
        
        # Create categories
        category1 = Category(name="Category 1", description="Category 1 description")
        category2 = Category(name="Category 2", description="Category 2 description")
        category_repository.save(category1)
        category_repository.save(category2)
        
        # Create a genre with 3 categories
        category3 = Category(name="Category 3", description="Category 3 description")
        category_repository.save(category3)
        
        genre = Genre(
            name="Action",
            is_active=True,
            categories={category1.id, category2.id, category3.id}
        )
        genre_repository.save(genre)
        
        use_case = UpdateGenre(
            repository=genre_repository,
            category_repository=category_repository,
        )
        
        # Act - Update with only 2 categories
        use_case.execute(UpdateGenre.Input(
            id=genre.id,
            name="Updated Genre",
            is_active=False,
            categories={category1.id, category2.id},
        ))
        
        # Assert
        updated_genre = genre_repository.get_by_id(genre.id)
        assert updated_genre.name == "Updated Genre"
        assert updated_genre.is_active is False
        assert updated_genre.categories == {category1.id, category2.id}
        # Ensure category3 is no longer associated
        assert category3.id not in updated_genre.categories