import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database.session import Base, get_db
from app.main import app

# Используем отдельную тестовую БД
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_autopilot.db"

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db():
    """Фикстура базы данных для тестов"""
    # Создаем таблицы для тестов
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
    # Очищаем после тестов
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db):
    """Фикстура тестового клиента"""

    def override_get_db():
        try:
            yield db
        finally:
            db.close()

    # Переопределяем зависимость БД
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    # Очищаем переопределения после теста
    app.dependency_overrides.clear()


# Добавляем фикстуру для Allure
@pytest.fixture(scope="function")
def allure_report():
    """Фикстура для Allure отчетов"""
    import allure

    with allure.step("Setup test"):
        yield
