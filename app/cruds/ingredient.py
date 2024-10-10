from app.schemas import IngredientCreate, IngredientUpdate, IngredientResponse
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from app.models import Ingredient
from datetime import datetime, timedelta

def find_all(db: Session):
    ingredients = db.query(Ingredient).order_by(Ingredient.date).all()
    return [IngredientResponse.from_orm(ingredient) for ingredient in ingredients]

def find_by_id(db: Session, id: int):
    return db.query(Ingredient).filter(id == Ingredient.id).first()

def find_by_safe(db: Session):
    now = datetime.now()
    ingredients = db.query(Ingredient).filter(
        or_(
            and_(Ingredient.tag == '消費期限', Ingredient.date >= now + timedelta(days=3)),
            and_(Ingredient.tag == '賞味期限', Ingredient.date >= now),
        )).order_by(Ingredient.date).all()
    return [IngredientResponse.from_orm(ingredient) for ingredient in ingredients]

def find_by_caution(db: Session):
    now = datetime.now()
    ingredients = db.query(Ingredient).filter(
        or_(
            and_(Ingredient.tag == '消費期限', Ingredient.date < now + timedelta(days=3), Ingredient.date >= now),
            and_(Ingredient.tag == '賞味期限', Ingredient.date < now)
        )).order_by(Ingredient.date).all()
    return [IngredientResponse.from_orm(ingredient) for ingredient in ingredients]

def find_by_limit(db: Session):
    ingredients = db.query(Ingredient).filter(Ingredient.tag == '消費期限').filter(
            Ingredient.date < datetime.now()
        ).order_by(Ingredient.date).all()
    return [IngredientResponse.from_orm(ingredient) for ingredient in ingredients]

def create(db: Session, ingredient_create: IngredientCreate):
    new_ingredient = Ingredient(**ingredient_create.model_dump())
    db.add(new_ingredient)
    db.commit()
    return new_ingredient

def update(db: Session, id: int, ingredient_update: IngredientUpdate):
    ingredient = find_by_id(db, id)
    if ingredient is None:
        return None
    ingredient.name = ingredient.name if ingredient_update.name is None else ingredient_update.name
    ingredient.date = ingredient.date if ingredient_update.date is None else ingredient_update.date
    ingredient.tag = ingredient.tag if ingredient_update.tag is None else ingredient_update.tag
    ingredient.amount = ingredient.amount if ingredient_update.amount is None else ingredient_update.amount
    ingredient.unit_majar = ingredient.unit_majar if ingredient_update.unit_majar is None else ingredient_update.unit_majar
    ingredient.description = ingredient.description if ingredient_update.description is None else ingredient_update.description

    db.add(ingredient)
    db.commit()
    return ingredient

def delete(db: Session, id: int):
    ingredient = find_by_id(db, id)
    if ingredient is None:
        return None
    db.delete(ingredient)
    db.commit()
    return ingredient