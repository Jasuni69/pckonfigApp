from fastapi import FastAPI
from app.api.endpoints import components

app = FastAPI()

app.include_router(components.router)
