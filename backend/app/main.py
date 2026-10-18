from fastapi import FastAPI
from app.routers.auth import router as auth_router
from app.routers.my_guide_updates import router as my_guide_updates_router

app = FastAPI()
app.include_router(auth_router)
app.include_router(my_guide_updates_router)


@app.get("/")
def root():
    return {"message": "Backend is running"}
