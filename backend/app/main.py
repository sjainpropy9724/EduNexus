from fastapi import FastAPI
from app.api import routes
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import router as api_router
from app.core.config import settings

app = FastAPI(title=settings.PROJECT_NAME)

# --- ADD THIS CORS BLOCK ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5174",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# ---------------------------

app.include_router(routes.router, prefix="/api/v1")

# Include the routes we just created
app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/")
def read_root():
    return {"message": "Edu-Nexus API is Running"}

@app.get("/health")
def health_check():
    return {"status": "active", "mode": "development"}