from fastapi import FastAPI
from app.routers.auth import router as auth_router
from app.routers.protected import router as protected_router

app = FastAPI()
app.include_router(auth_router)
app.include_router(protected_router)


@app.get("/")
def root():
    return {"message": "Backend is running"}
