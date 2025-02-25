from pydantic import BaseModel, ConfigDict, Field


class BaseRecipe(BaseModel):
    """Базовая модель рецепта"""

    title: str = Field(..., title="Title of the recipe", example="Пельмени")
    cooking_time: float = Field(..., title="Cooking time", example=20.0)
    ingredients: str = Field(
        ..., title="the ingredients for the recipe", example="Мясо, мука..."
    )
    description: str = Field(
        ...,
        title="description of the dish preparation",
        example="Кинуть пельмени в кипящую воду и подождать 20 мин.",
    )


class RecipeIn(BaseRecipe):
    """Модель для создания нового рецепта"""

    ...


class RecipeOut(BaseRecipe):
    """Модель для вывода информации о добавленном рецепте"""

    id: int = Field(..., title="Id of the recipe")
    number_of_views: int = Field(
        ..., title="number of views"
    )  # Количество просмотров рецепта
    model_config = ConfigDict(strict=True)


class RecipeAll(BaseModel):
    """Модель для вывода списка всех рецептов"""

    title: str = Field(..., title="Title of the recipe", example="Пельмени")
    number_of_views: int = Field(..., title="number of views")
    cooking_time: float = Field(..., title="Cooking time", example=20.0)
    model_config = ConfigDict(strict=True)
