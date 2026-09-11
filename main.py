from fastapi import FastAPI
from recipe import router

app = FastAPI()

app.include_router(router)