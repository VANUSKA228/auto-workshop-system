# backend/app/main.py
"""
Точка входа FastAPI-приложения.
Подключает роутеры, настраивает CORS и глобальные обработчики.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import get_settings
from .routers import auth, orders, users, services, payments, reports

settings = get_settings()

app = FastAPI(
    title="API автосервиса",
    description="REST API для системы управления автосервисом (ТЗ v2.0)",
    version="1.0.0",
)

# CORS — разрешаем запросы с фронтенда. ТЗ: в продакшене только домен фронта.
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключаем роутеры. Префиксы задаются в каждом роутере.
app.include_router(auth.router, prefix="/auth", tags=["Авторизация"])
app.include_router(orders.router, prefix="/orders", tags=["Заявки"])
app.include_router(users.router, prefix="/users", tags=["Пользователи"])
app.include_router(services.router, prefix="/services", tags=["Услуги"])
app.include_router(payments.router, prefix="/payments", tags=["Платежи"])
app.include_router(reports.router, prefix="/reports", tags=["Отчёты"])


@app.get("/")
def root():
    """Health-check и информация об API."""
    return {"message": "API автосервиса", "docs": "/docs"}


@app.get("/health")
def health():
    """Проверка доступности сервиса для Docker/monitoring."""
    return {"status": "ok"}
