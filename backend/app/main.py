from fastapi import FastAPI
from app.routers.auth import router as auth_router
from app.routers.my_guides import router as my_guides_router

app = FastAPI()
app.include_router(auth_router)
app.include_router(my_guides_router)


@app.get("/")
def root():
    return {"message": "Backend is running"}
