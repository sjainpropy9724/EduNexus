from fastapi import FastAPI
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import router as api_router
from app.core.config import settings
from app.services.graph_builder import graph_builder

# ── Lifespan: handles startup and shutdown cleanly ────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("🚀 Edu-Nexus V2 starting up...")
    print(f"   Neo4j: {settings.NEO4J_URI}")
    yield
    # Shutdown
    print("🛑 Shutting down — closing Neo4j driver...")
    graph_builder.close()

# ── App ───────────────────────────────────────────────────────────────────────
app = FastAPI(
    title=settings.PROJECT_NAME,
    version="2.0.0",
    lifespan=lifespan
)

# ── CORS ──────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # V1 frontend
        "http://localhost:5174",  # V2 frontend
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routes (registered ONCE — bug fixed) ─────────────────────────────────────
app.include_router(api_router, prefix=settings.API_V1_STR)

# ── Root endpoints ────────────────────────────────────────────────────────────
@app.get("/")
def read_root():
    return {"message": "Edu-Nexus V2 API is Running", "version": "2.0.0"}

@app.get("/health")
def health_check():
    try:
        with graph_builder.driver.session() as session:
            session.run("RETURN 1")
            neo4j_status = "connected"
    except Exception as e:
        neo4j_status = f"error: {str(e)}"
    
    return {
        "status": "active",
        "version": "2.0.0",
        "neo4j": neo4j_status,
        "mode": "development"
    }
