from fastapi import FastAPI

from FastAPI.src.first_steps.router import router

app = FastAPI()

app.include_router(router)