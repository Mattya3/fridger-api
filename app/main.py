from fastapi import FastAPI
from app.routing import ingredient 

app = FastAPI()

app.include_router(ingredient.router)