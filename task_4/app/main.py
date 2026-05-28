from fastapi import FastAPI
from app.routers import tasks, users, admin

app = FastAPI()

app.include_router(tasks.router)
app.include_router(users.router)
app.include_router(admin.router)

@app.get("/health")
def health_check():
    return {"status": "ok"}