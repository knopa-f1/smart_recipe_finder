from fastapi import APIRouter, Depends, HTTPException, Query

from app.api.schemas.recipe import RecipeCreate, RecipeUpdate, RecipeOut
from app.services.recipe_service import RecipeService
from app.utils.unitofwork import UnitOfWork

router = APIRouter(prefix="/recipes", tags=["recipes"])


def get_service() -> RecipeService:
    return RecipeService(UnitOfWork())


@router.post("/", response_model=RecipeOut)
async def create_recipe(
    recipe_in: RecipeCreate,
    service: RecipeService = Depends(get_service),
):
    return await service.create_recipe(recipe_in)


@router.get("/{recipe_id}", response_model=RecipeOut)
async def get_recipe(
    recipe_id: int,
    service: RecipeService = Depends(get_service),
):
    recipe = await service.get_recipe(recipe_id)
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")
    return recipe


@router.get("/", response_model=list[RecipeOut])
async def list_recipes(
    skip: int = 0,
    limit: int = 20,
    service: RecipeService = Depends(get_service),
):
    return await service.list_recipes(skip=skip, limit=limit)


@router.put("/{recipe_id}", response_model=RecipeOut)
async def update_recipe(
    recipe_id: int,
    recipe_in: RecipeUpdate,
    service: RecipeService = Depends(get_service),
):
    recipe = await service.update_recipe(recipe_id, recipe_in)
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")
    return recipe


@router.delete("/{recipe_id}")
async def delete_recipe(
    recipe_id: int,
    service: RecipeService = Depends(get_service),
):
    deleted = await service.delete_recipe(recipe_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Recipe not found")
    return {"status": "deleted"}


@router.get("/filter/", response_model=list[RecipeOut])
async def filter_recipes(
    include: list[str]|None = Query(None),
    exclude: list[str]|None = Query(None),
    service: RecipeService = Depends(get_service),
):
    return await service.filter_by_ingredients(include=include, exclude=exclude)

@router.get("/search/", response_model=list[RecipeOut])
async def search_recipes(
    q: str = Query(..., description="Natural language query"),
    service: RecipeService = Depends(get_service),
):
    return await service.search(q)
