from fastapi import FastAPI
from app.api.routes import router

app = FastAPI(title="AI Studio MVP")
app.include_router(router)
