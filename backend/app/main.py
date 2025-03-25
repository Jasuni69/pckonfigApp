from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.endpoints import components, auth, optimize

app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(components.router, prefix="/api")
app.include_router(auth.router, prefix="/api/auth")
app.include_router(optimize.router, prefix="/api/optimize")
