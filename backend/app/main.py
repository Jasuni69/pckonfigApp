from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.endpoints import components, auth, optimize
import threading
import os
import sys

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import and run ChromaDB population script
try:
    # Add the parent directory to sys.path
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    
    from ChromaDB.populate import populate_chroma
    # Run in a separate thread to not block startup
    threading.Thread(target=populate_chroma).start()
    print("ChromaDB population started in background")
except Exception as e:
    print(f"Error starting ChromaDB population: {str(e)}")

app.include_router(components.router, prefix="/api")
app.include_router(auth.router, prefix="/api/auth")
app.include_router(optimize.router, prefix="/api/optimize")
