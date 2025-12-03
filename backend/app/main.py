from fastapi import FastAPI, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from typing import AsyncGenerator
import logging
import os
from datetime import datetime

from .config.database import engine, Base
from .config.settings import settings
from .utils.scheduler import GoalScheduler
from .utils.validators import ValidationException

# Import routes directly
from .routes import auth, transactions, dashboard, predictions, goals, badges

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

scheduler = GoalScheduler()

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    logger.info("Starting up SpendWise application...")
    
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created")
    
    scheduler.start()
    logger.info("Background scheduler started")
    
    yield
    
    logger.info("Shutting down SpendWise application...")
    scheduler.shutdown()

app = FastAPI(
    title="SpendWise - Personal Finance API",
    description="A modern personal finance application with budget prediction and gamification",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.exception_handler(ValidationException)
async def validation_exception_handler(request: Request, exc: ValidationException):
    return JSONResponse(
        status_code=400,
        content={"detail": str(exc)},
    )

# Include API routes
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(transactions.router, prefix="/api/v1/transactions", tags=["Transactions"])
app.include_router(dashboard.router, prefix="/api/v1/dashboard", tags=["Dashboard"])
app.include_router(predictions.router, prefix="/api/v1/predictions", tags=["Predictions"])
app.include_router(goals.router, prefix="/api/v1/goals", tags=["Savings Goals"])
app.include_router(badges.router, prefix="/api/v1/badges", tags=["Badges"])

@app.get("/")
async def root():
    return {
        "message": "Welcome to SpendWise API",
        "version": "1.0.0",
        "documentation": "/docs",
        "status": "running"
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )