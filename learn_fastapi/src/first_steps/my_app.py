from fastapi import FastAPI
from learn_fastapi.src.first_steps.router import router

app = FastAPI()

app.include_router(router)
