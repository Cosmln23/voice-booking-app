#!/usr/bin/env python3
"""
Simple health check script pentru debugging
"""

import asyncio
from fastapi import FastAPI
import uvicorn

# Create minimal FastAPI app
app = FastAPI(title="Simple Health Test")

@app.get("/health")
async def health_check():
    """Minimal health endpoint"""
    return {"status": "ok", "message": "Simple health check working"}

@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "Simple FastAPI is running"}

if __name__ == "__main__":
    print("Starting simple health server on port 8000...")
    uvicorn.run(
        "simple_health:app",
        host="0.0.0.0", 
        port=8000,
        log_level="info"
    )