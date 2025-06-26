from unittest.mock import patch
import pytest
from rest_framework.test import APIClient
from src.config import DEFAULT_PAGINATION_SIZE
from src.django_project.category_app.views import CategoryViewSet


@pytest.fixture
def api_client() -> APIClient:
    return APIClient()


@pytest.mark.django_db
class TestCreateAndEditCategory:
    @patch.object(CategoryViewSet, "permission_classes", [])
    def test_user_can_create_and_edit_category(self, api_client: APIClient) -> None:
        # Acessa listagem e verifica que não tem nenhuma categoria criada
        list_response = api_client.get("/api/categories/")
        assert list_response.data == {
            "data": [],
            "meta": {
                "current_page": 1,
                "per_page": DEFAULT_PAGINATION_SIZE,
                "total": 0,
            }
        }

        # Cria uma categoria
        create_response = api_client.post(
            "/api/categories/",
            {
                "name": "Movie",
                "description": "Movie description",
            },
        )
        assert create_response.status_code == 201
        created_category_id = create_response.data["id"]

        # Verifica que categoria criada aparece na listagem
        assert api_client.get("/api/categories/").data == {
            "data": [
                {
                    "id": created_category_id,
                    "name": "Movie",
                    "description": "Movie description",
                    "is_active": True,
                }
            ],
            "meta": {
                "current_page": 1,
                "per_page": DEFAULT_PAGINATION_SIZE,
                "total": 1,
            },
        }

        # Edita categoria criada
        edit_response = api_client.put(
            f"/api/categories/{created_category_id}/",
            {
                "name": "Documentary",
                "description": "Documentary description",
                "is_active": True,
            },
        )
        assert edit_response.status_code == 204

        # Verifica que categoria editada aparece na listagem
        api_client.get("/api/categories/").data == {
            "data": [
                {
                    "id": created_category_id,
                    "name": "Documentary",
                    "description": "Documentary description",
                    "is_active": True,
                }
            ]
        }
