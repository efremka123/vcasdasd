"""
StudentFlow API - Smart personal finance tracker for students.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from backend.models.database import init_db
from backend.routers.transactions import router as transactions_router
from backend.routers.finance import router as finance_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager - handles startup and shutdown events."""
    # Initialize database on startup
    init_db()
    yield
    # Cleanup on shutdown (if needed)


def create_app() -> FastAPI:
    """Application factory for creating FastAPI instance."""
    app = FastAPI(
        title="StudentFlow",
        description="Smart personal finance tracker for students",
        version="0.1.0",
        lifespan=lifespan
    )

    # Configure CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # TODO: Specify concrete domains in production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include routers
    app.include_router(transactions_router)
    app.include_router(finance_router)

    # Register routes
    @app.get("/")
    def root():
        """Root endpoint."""
        return {
            "message": "Welcome to StudentFlow API 🎓",
            "docs": "/docs",
            "version": "0.1.0"
        }

    @app.get("/health")
    def health_check():
        """Health check endpoint."""
        return {"status": "ok"}

    return app


# Create application instance
app = create_app()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
