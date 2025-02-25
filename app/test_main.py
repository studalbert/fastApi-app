from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_get_all_recipes():
    response = client.get("/recipes")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_create_recipe():
    response = client.post(
        "/recipes",
        json={
            "title": "Пельмени",
            "cooking_time": 20.0,
            "ingredients": "Мука, вода, мясо",
            "description": "Вкусные пельмени.",
        },
    )

    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Пельмени"
    assert data["cooking_time"] == 20.0


def test_create_recipe_with_error():
    response = client.post(
        "/recipes",
        json={
            "title": "Пельмени",
            "cooking_time": "string",
            "ingredients": "Мука, вода, мясо",
            "description": "Вкусные пельмени.",
        },
    )

    assert response.status_code == 422


def test_get_recipe_by_id():
    response = client.get("/recipes/2")
    data = response.json()
    assert response.status_code == 200
    assert isinstance(data, dict)
    assert data["id"] == 2


def test_get_recipe_by_id_with_error():

    response = client.get("/recipes/str")
    assert response.status_code == 422

    response = client.get("/recipes/1000")
    assert response.status_code == 404
