from fastapi import FastAPI
from app.routers import login, garden, question
from app.scripts import iFlyTek_ASR

app = FastAPI()

app.include_router(login.router, tags=["login"])
app.include_router(garden.router, tags=["garden"])
app.include_router(question.router, tags=["question"])
app.include_router(iFlyTek_ASR.router, tags=["audio"])

@app.get("/")
def read_root():
    return {"message": "Welcome to FastAPI!"}