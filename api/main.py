from fastapi import FastAPI

from src.actors.routes import router as actors_router
from src.movies.routes import router as movies_router
from core.config import settings

app = FastAPI(
    title= settings.PROJECT_NAME
)

app.include_router(actors_router)
app.include_router(movies_router)

@app.get("/")
def read_root():
    return {"message": "Hello from IMDB API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}