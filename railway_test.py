#!/usr/bin/env python3
"""
Ultra minimal Railway test - doar health endpoint
"""

from fastapi import FastAPI
import uvicorn

app = FastAPI()

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/")
def root():
    return {"message": "Railway test"}

if __name__ == "__main__":
    uvicorn.run("railway_test:app", host="0.0.0.0", port=8000)