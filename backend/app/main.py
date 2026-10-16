from fastapi import FastAPI
from app.routers.auth import router as auth_router
from app.routers.tu_auth import router as tu_auth_router

app = FastAPI()
app.include_router(auth_router)
app.include_router(tu_auth_router)


@app.get("/")
def root():
    return {"message": "Backend is running"}
