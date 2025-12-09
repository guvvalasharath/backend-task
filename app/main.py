from fastapi import FastAPI
from app.routers import auth, users, tasks

app = FastAPI(title="Task Management API")

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(tasks.router)

@app.get("/")
async def root():
    return {"status": "ok"}
