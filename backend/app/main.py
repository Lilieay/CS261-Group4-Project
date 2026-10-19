from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers.auth import router as auth_router
from app.routers.courses import router as courses_router
from app.routers.guides import router as guides_router
from app.routers.my_guide_deletions import router as my_guide_deletions_router
from app.routers.my_guide_updates import router as my_guide_updates_router
from app.routers.my_guides import router as my_guides_router

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5000", "http://localhost:5000"],
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)
app.include_router(auth_router)
app.include_router(courses_router)
app.include_router(guides_router)
app.include_router(my_guide_deletions_router)
app.include_router(my_guide_updates_router)
app.include_router(my_guides_router)


@app.get("/")
def root():
    return {"message": "Backend is running"}
