from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import get_settings
from .routers import auth, workshops

settings = get_settings()

app = FastAPI(
    title="API автосервиса",
    description="REST API для авторизации и регистрации",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/auth", tags=["Авторизация"])
app.include_router(workshops.router, prefix="/workshops", tags=["Мастерские"])


@app.get("/")
def root():
    return {"message": "API автосервиса — Версия 1 (auth-only)", "docs": "/docs"}


@app.get("/health")
def health():
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
