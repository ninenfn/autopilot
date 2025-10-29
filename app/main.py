from fastapi import FastAPI
from app.database.session import engine, Base
from app.api.drivers import router as drivers_router

# Создание таблиц
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="AutoPilot API",
    description="API для сервиса поиска водителей для личного авто",
    version="1.0.0"
)

# Подключение роутеров
app.include_router(drivers_router)

@app.get("/")
async def root():
    return {"message": "Welcome to AutoPilot API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)