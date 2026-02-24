from fastapi import FastAPI

from .router import router
from ..middleware import register_dev_reload

app = FastAPI()

app.include_router(router)
register_dev_reload(app)
