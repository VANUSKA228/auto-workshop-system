# backend/app/main.py
"""
Точка входа FastAPI-приложения.
Подключает роутеры, настраивает CORS и глобальные обработчики.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import get_settings
from .routers import auth, orders, users, services, payments, workshops, workers

settings = get_settings()

app = FastAPI(
    title="API автосервиса",
    description="REST API для системы управления автосервисом (ТЗ v2.0)",
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
app.include_router(orders.router, prefix="/orders", tags=["Заявки"])
app.include_router(users.router, prefix="/users", tags=["Пользователи"])
app.include_router(services.router, prefix="/services", tags=["Услуги"])
app.include_router(payments.router, prefix="/payments", tags=["Платежи"])
app.include_router(workshops.router, prefix="/workshops", tags=["Мастерские"])
app.include_router(workers.router, prefix="/workers", tags=["Работники"])


@app.get("/")
def root():
    return {"message": "API автосервиса", "docs": "/docs"}


@app.get("/health")
def health():
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
