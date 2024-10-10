from typing import Optional, List
from fastapi import APIRouter, Body, Path, Query, HTTPException, Depends
from app.cruds import ingredient as ingredient_cruds
from app.schemas import IngredientCreate, IngredientUpdate, IngredientReqResponse, IngredientResponse
from starlette import status
from sqlalchemy.orm import Session
from app.database import get_db
from typing import Annotated

DbDependency = Annotated[Session, Depends(get_db)]

router = APIRouter(prefix="/Ingredients", tags=["Ingredients"])

@router.get("", response_model=List[IngredientResponse], status_code=status.HTTP_200_OK)
async def find_all(db: DbDependency):
    return ingredient_cruds.find_all(db)

@router.get("/green", response_model=List[IngredientResponse], status_code=status.HTTP_200_OK)
async def find_by_limit(db: DbDependency):
    return ingredient_cruds.find_by_safe(db)

@router.get("/yellow", response_model=List[IngredientResponse], status_code=status.HTTP_200_OK)
async def find_by_limit(db: DbDependency):
    return ingredient_cruds.find_by_caution(db)

@router.get("/red", response_model=List[IngredientResponse], status_code=status.HTTP_200_OK)
async def find_by_limit(db: DbDependency):
    return ingredient_cruds.find_by_limit(db)

@router.post("", response_model=IngredientReqResponse, status_code=status.HTTP_200_OK)
async def create(db: DbDependency, ingredient_create: IngredientCreate):
    return ingredient_cruds.create(db, ingredient_create)

@router.put("/{id}", response_model=IngredientReqResponse, status_code=status.HTTP_200_OK)
async def update(db: DbDependency, ingredient_update: IngredientUpdate, id: int=Path(gt=0)):
    update_ingredient = ingredient_cruds.update(db, id, ingredient_update)
    if update_ingredient is None:
        raise HTTPException(status_code=400, detail="ingredient not found")
    return update_ingredient

@router.delete("/{id}", response_model=IngredientReqResponse, status_code=status.HTTP_200_OK)
async def delete(db: DbDependency, id: int=Path(gt=0)):
    delete_ingredient = ingredient_cruds.delete(db, id)
    if delete_ingredient is None:
        raise HTTPException(status_code=400, detail="ingredient not found")
    return delete_ingredient