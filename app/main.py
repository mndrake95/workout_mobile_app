from fastapi import FastAPI
from app.routers import users, exercises

app = FastAPI()

app.include_router(users.router)
app.include_router(exercises.router)

@app.get("/")
async def root():
    return {"message": "Hello World"}

