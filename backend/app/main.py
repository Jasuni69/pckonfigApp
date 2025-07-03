from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.endpoints import components, auth, optimize
import threading
import os
import sys
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

# Rate limiting setup
limiter = Limiter(key_func=get_remote_address)

app = FastAPI()

# Add rate limiting middleware
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Improved CORS configuration
allowed_origins = [
    "http://localhost:3000",  # React dev server
    "http://localhost:5173",  # Vite dev server
    "http://localhost:80",    # Production frontend
    # Add your production domain here
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,  # Restrict to specific origins
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],  # Be specific about methods
    allow_headers=["*"],
)

# Import and run ChromaDB population script
try:
    # Add the parent directory to sys.path
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    
    from ChromaDB.populate import populate_chroma
    
    def safe_populate_chroma():
        """Safely populate ChromaDB with error handling"""
        try:
            populate_chroma()
            print("ChromaDB population completed successfully")
        except Exception as e:
            print(f"Warning: ChromaDB population failed: {str(e)}")
            print("API will continue to work without ChromaDB features")
    
    # Run in a separate thread to not block startup
    threading.Thread(target=safe_populate_chroma, daemon=True).start()
    print("ChromaDB population started in background")
except Exception as e:
    print(f"Warning: Could not start ChromaDB population: {str(e)}")
    print("API will continue to work without ChromaDB features")

app.include_router(components.router, prefix="/api")
app.include_router(auth.router, prefix="/api/auth")
app.include_router(optimize.router, prefix="/api/optimize")
