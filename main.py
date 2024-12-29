from fastapi import FastAPI
from routers import api_routers as api_rout

app = FastAPI()

app.router.include_router(api_rout.router)
