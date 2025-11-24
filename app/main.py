from fastapi import FastAPI

from app.api.drivers import router as drivers_router
from app.database.session import Base, engine

# Создание таблиц
Base.metadata.create_all(bind=engine)

app: FastAPI = FastAPI(
    title="AutoPilot API",
    description="API для сервиса поиска водителей для личного авто",
    version="1.0.0",
)

# Подключение роутеров
app.include_router(drivers_router)


@app.get("/")
async def root() -> dict[str, str]:
    return {"message": "Welcome to AutoPilot API"}


@app.get("/health")
async def health_check() -> dict[str, str]:
    return {"status": "healthy"}


def run_app() -> None:
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)


if __name__ == "__main__":
    run_app()
