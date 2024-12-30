from fastapi import FastAPI
from app.server.routes import router as HabitRouter
from fastapi.middleware.cors import CORSMiddleware
origins = [
    "http://localhost:3000"
]
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(HabitRouter, tags=["Habit"], prefix="/habits")

@app.get("/", tags=["Root"])
async def read_root():
    return {"message": "Welcome to this app!"}