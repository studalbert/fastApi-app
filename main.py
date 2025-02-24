from contextlib import asynccontextmanager
from typing import List

import uvicorn
from fastapi import FastAPI, HTTPException, status, Depends
from sqlalchemy import desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

import models
import schemas
from database import engine, async_session
from typing import Annotated
from fastapi.params import Path


# @app.on_event("startup")
# async def shutdown():
#     async with engine.begin() as conn:
#         await conn.run_sync(models.Base.metadata.create_all)
#
#
# @app.on_event("shutdown")
# async def shutdown():
#     await session.close()
#     await engine.dispose()


@asynccontextmanager
async def lifespan(app: FastAPI):

    async with engine.begin() as conn:
        await conn.run_sync(models.Base.metadata.create_all)  # Создание таблиц
    yield
    await engine.dispose()  # Освобождение ресурсов движка базы данных


app = FastAPI(
    lifespan=lifespan,
    openapi_tags=[{"name": "recipes", "description": "Operations with recipes."}],
)


async def get_session() -> AsyncSession:
    async with async_session() as session:
        yield session


@app.get("/recipes", response_model=List[schemas.RecipeAll], tags=["recipes"])
async def get_all_recipes(
    session: AsyncSession = Depends(get_session),
) -> List[models.Recipe]:
    """
    Получить список всех рецептов.
    Рецепты отсортированы по количеству просмотров.
    """
    res = await session.execute(
        select(
            models.Recipe
            # models.Recipe.title,
            # models.Recipe.number_of_views,
            # models.Recipe.cooking_time,
        ).order_by(desc(models.Recipe.number_of_views), models.Recipe.cooking_time)
    )
    return res.scalars().all()


@app.get("/recipes/{recipe_id}", response_model=schemas.RecipeOut, tags=["recipes"])
async def get_recipe_by_id(
    recipe_id: Annotated[int, Path(title="Id of the recipe", ge=1)],
    session: AsyncSession = Depends(get_session),
) -> models.Recipe:
    """
    Получить рецепт по ID.

    - **recipe_id**: Уникальный идентификатор рецепта.
    """
    result = await session.execute(
        select(models.Recipe).where(models.Recipe.id == recipe_id)
    )
    recipe = result.scalar_one_or_none()

    if recipe is None:
        raise HTTPException(status_code=404, detail="Recipe not found")

    recipe.number_of_views += 1
    await session.commit()
    await session.refresh(recipe)
    return recipe


@app.post(
    "/recipes",
    response_model=schemas.RecipeOut,
    status_code=status.HTTP_201_CREATED,
    tags=["recipes"],
)
async def post_recipe(
    recipe: schemas.RecipeIn,
    session: AsyncSession = Depends(get_session),
) -> models.Recipe:
    """
    Создать новый рецепт.

    - **title**: Название рецепта.
    - **cooking_time**: Время приготовления (в минутах).
    - **ingredients**: Ингредиенты.
    - **description**: Описание рецепта.
    """
    new_recipe = models.Recipe(**recipe.model_dump())
    async with session.begin():
        session.add(new_recipe)
    return new_recipe


@app.delete(
    "/recipes/{recipe_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["recipes"]
)
async def delete_recipe_by_id(
    recipe_id: Annotated[int, Path(title="Id of the recipe", ge=1)],
    session: AsyncSession = Depends(get_session),
):
    """
    Удалить рецепт по ID.

    - **recipe_id**: Уникальный идентификатор рецепта.
    """
    result = await session.execute(
        select(models.Recipe).where(models.Recipe.id == recipe_id)
    )
    recipe = result.scalar_one_or_none()

    if recipe is None:
        raise HTTPException(status_code=404, detail="Recipe not found")

    await session.delete(recipe)
    await session.commit()


if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)
