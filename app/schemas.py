from typing import Optional
from enum import Enum
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime, timedelta

class IngredientCreate(BaseModel):
    name: str = Field(min_length=1, max_length=20, examples=["example"])
    date: datetime
    tag: str =  Field(default="賞味期限", examples=["賞味期限"])
    amount: int = Field(gt=0, examples=[100])
    unit_majar: Optional[str] = Field(default=None, examples=["g"])
    description: Optional[str] = Field(default=None, examples=["this is a example"])

class IngredientUpdate(BaseModel):
    name: str = Field(default=None, min_length=1, max_length=20, examples=["example"])
    date: datetime = Field(default=None)
    tag: str =  Field(default="賞味期限", examples=["賞味期限"])
    amount: int = Field(default=None, gt=0, examples=[100])
    unit_majar: Optional[str] = Field(default=None, examples=["g"])
    description: Optional[str] = Field(default=None, examples=["this is a example"])

class IngredientReqResponse(BaseModel):
    id: int = Field(gt=0, examples=[1])
    name: str = Field(min_length=1, max_length=20, examples=["example"])
    date: datetime
    tag: str =  Field(examples=["賞味期限"])
    amount: int = Field(gt=0, examples=[100])
    unit_majar: Optional[str] = Field(examples=["g"])
    description: Optional[str] = Field(examples=["this is a example"])
    #created_at: datetime
    #updated_at: datetime
    model_config = ConfigDict(from_attributes=True)

class IngredientResponse(BaseModel):
    id: int = Field(gt=0, examples=[1])
    name: str = Field(min_length=1, max_length=20, examples=["example"])
    date: datetime
    tag: str =  Field(examples=["賞味期限"])
    amount: int = Field(gt=0, examples=[100])
    unit_majar: Optional[str] = Field(examples=["g"])
    description: Optional[str] = Field(examples=["this is a example"])
    #created_at: datetime
    #updated_at: datetime
    state: str

    class Config:
        orm_mode = True

    @classmethod
    def from_orm(cls, ingredient):
        now = datetime.now()
        three_days_from_now = now + timedelta(days=3)
        if ingredient.date < now and ingredient.tag == "消費期限":
            state = "red"
        elif (ingredient.date < three_days_from_now and ingredient.tag == "消費期限") or  (ingredient.date < now and ingredient.tag == "賞味期限"):
            state = "yellow"
        else:
            state = "green"
        return cls(**ingredient.__dict__, state=state)
    