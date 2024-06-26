from fastapi import FastAPI
from app.routers import login, garden, question

app = FastAPI()

app.include_router(login.router, tags=["login"])
app.include_router(garden.router, tags=["garden"])
app.include_router(question.router, tags=["question"])

@app.get("/")
def read_root():
    return {"message": "Welcome to FastAPI!"}
