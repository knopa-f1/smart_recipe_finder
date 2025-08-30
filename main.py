import uvicorn
from fastapi import FastAPI

from app.api.endpoints import recipes

app = FastAPI()

app.include_router(recipes.router)


@app.get("/")
async def read_root():
    return {"message": "Welcome to the Smart Recipe Finder API server"}


if __name__ == "__main__":
    uvicorn.run(app="main:app", reload=True)
