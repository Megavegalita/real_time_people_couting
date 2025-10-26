"""
Main FastAPI Application

This is the main entry point for the Gender Analysis API.
It initializes the FastAPI app, includes routers, and sets up middleware.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# Import routers
# from api.endpoints import health, camera, results

from config.settings import settings

# Create FastAPI application
app = FastAPI(
    title="Gender Analysis API",
    description="Multi-Camera Gender & Age Detection System",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO: Configure properly
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
# app.include_router(health.router, prefix="/health", tags=["health"])
# app.include_router(camera.router, prefix="/camera", tags=["camera"])
# app.include_router(results.router, prefix="/results", tags=["results"])

@app.get("/")
async def root():
    """
    Root endpoint providing API information.
    
    Returns:
        JSON response with API metadata
    """
    return JSONResponse({
        "name": "Gender Analysis API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs"
    })


@app.get("/config")
async def get_config():
    """
    Get current configuration (without sensitive data).
    
    Returns:
        Configuration information
    """
    return JSONResponse({
        "api": {
            "host": settings.api.host,
            "port": settings.api.port,
            "workers": settings.api.workers
        },
        "processing": {
            "batch_size": settings.processing.batch_size,
            "max_workers": settings.processing.max_workers
        },
        "models": {
            "face_detection": settings.face_detection.model,
            "feature_extraction": settings.feature_extraction.model,
            "gender_model": settings.gender_classification.model
        }
    })


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "api.main:app",
        host=settings.api.host,
        port=settings.api.port,
        reload=settings.api.reload,
        workers=settings.api.workers
    )

