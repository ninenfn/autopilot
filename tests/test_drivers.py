from unittest.mock import patch

import pytest

from app.models.domain.driver import DriverStatus
from app.models.schemas.driver import DriverCreateRequest


class TestDriversAPI:
    """Unit-тесты для API водителей"""

    def test_create_driver_success(self, client):
        """Тест успешного создания водителя"""
        driver_data = {
            "user_id": 1,
            "license_number": "AB123456",
            "years_of_experience": 5,
        }

        response = client.post("/drivers/", json=driver_data)

        assert response.status_code == 201
        data = response.json()
        assert data["license_number"] == driver_data["license_number"]
        assert data["status"] == DriverStatus.PENDING.value
        assert data["years_of_experience"] == 5
        assert "id" in data

    def test_create_driver_duplicate_license(self, client):
        """Тест создания водителя с дублирующимся номером прав"""
        driver_data = {
            "user_id": 1,
            "license_number": "DUPLICATE123",
            "years_of_experience": 3,
        }

        # Первый запрос должен быть успешным
        response1 = client.post("/drivers/", json=driver_data)
        assert response1.status_code == 201

        # Второй запрос с тем же номером прав должен вернуть ошибку
        response2 = client.post("/drivers/", json=driver_data)
        assert response2.status_code == 400 or response2.status_code == 409

    def test_create_driver_validation_error(self, client):
        """Тест валидации данных"""
        invalid_data = {
            "user_id": 0,  # Invalid: must be positive
            "license_number": "AB",  # Too short
            "years_of_experience": 60,  # Too high
        }

        response = client.post("/drivers/", json=invalid_data)
        assert response.status_code == 422  # Validation error

    def test_get_drivers_empty(self, client):
        """Тест получения пустого списка водителей"""
        response = client.get("/drivers/")

        assert response.status_code == 200
        assert response.json() == []

    def test_get_drivers_with_data(self, client):
        """Тест получения списка водителей с данными"""
        # Создаем тестового водителя
        driver_data = {
            "user_id": 2,
            "license_number": "CD789012",
            "years_of_experience": 3,
        }
        client.post("/drivers/", json=driver_data)

        # Получаем список
        response = client.get("/drivers/")

        assert response.status_code == 200
        drivers = response.json()
        assert len(drivers) == 1
        assert drivers[0]["license_number"] == "CD789012"
        assert drivers[0]["status"] == "PENDING"

    def test_get_drivers_with_filter(self, client):
        """Тест фильтрации водителей по статусу"""
        # Создаем тестового водителя
        driver_data = {
            "user_id": 3,
            "license_number": "EF345678",
            "years_of_experience": 7,
        }
        client.post("/drivers/", json=driver_data)

        # Фильтруем по статусу PENDING
        response = client.get("/drivers/?status=PENDING")

        assert response.status_code == 200
        drivers = response.json()
        assert len(drivers) >= 1
        assert all(driver["status"] == "PENDING" for driver in drivers)


class TestDriversAPIErrorHandling:
    """Тесты обработки ошибок в API"""

    def test_create_driver_service_exception(self, client):
        """Тест обработки исключения из сервиса при создании"""
        with patch("app.api.drivers.DriverService.create_driver") as mock:
            mock.side_effect = Exception("Service broken")

            response = client.post(
                "/drivers/",
                json={
                    "user_id": 1,
                    "license_number": "ERROR123",
                    "years_of_experience": 5,
                },
            )

            assert response.status_code == 500

    def test_get_drivers_service_exception(self, client):
        """Тест обработки исключения из сервиса при получении"""
        with patch("app.api.drivers.DriverService.get_drivers") as mock:
            mock.side_effect = Exception("DB error")
            response = client.get("/drivers/")

            assert response.status_code == 500

    def test_create_driver_integrity_error(self, client):
        """Тест обработки IntegrityError при создании водителя"""
        from sqlalchemy.exc import IntegrityError

        with patch("app.api.drivers.DriverService.create_driver") as mock_create:
            mock_create.side_effect = IntegrityError(
                "mock", "mock", Exception("Unique constraint violated")
            )

            driver_data = {
                "user_id": 1,
                "license_number": "DUPLICATE123",
                "years_of_experience": 5,
            }

            response = client.post("/drivers/", json=driver_data)

            assert response.status_code == 409
            assert "already exists" in response.json()["detail"]

    def test_get_drivers_exception_handling(self, db):
        """Тест обработки исключений при получении водителей"""
        from app.services.driver_service import DriverService

        # Мокаем query напрямую из переданной сессии db
        with patch.object(db, "query") as mock_query:
            mock_query.side_effect = Exception("DB query failed")

            # Должен пробросить исключение
            with pytest.raises(Exception, match="DB query failed"):
                DriverService.get_drivers(db)

    def test_create_driver_missing_id(self, client):
        """Тест создания водителя с отсутствующим ID"""
        with patch("app.api.drivers.DriverService.create_driver") as mock_create:
            # Создаем driver с None id
            from app.models.domain.driver import Driver

            driver_without_id = Driver(
                id=None,  # ID отсутствует
                user_id=1,
                license_number="NOID123",
                years_of_experience=5,
                status=DriverStatus.PENDING,
            )
            mock_create.return_value = driver_without_id

            response = client.post(
                "/drivers/",
                json={"user_id": 1, "license_number": "NOID123", "years_of_experience": 5},
            )

            assert response.status_code == 500
            # Проверяем что вернулась ошибка 500 (любая)
            assert response.status_code == 500


class TestDriverService:
    """Unit-тесты для сервиса водителей"""

    def test_driver_domain_logic(self):
        """Тест бизнес-логики domain модели"""
        from app.models.domain.driver import Driver

        driver = Driver(user_id=1, license_number="TEST123", years_of_experience=2)

        # Тестируем отклонение
        driver.reject()
        assert driver.status == DriverStatus.REJECTED

    def test_driver_verification_validation(self):
        """Тест валидации при верификации"""
        from app.models.domain.driver import Driver

        driver = Driver(user_id=1, license_number="TEST123", years_of_experience=0)  # Меньше 1 года

        # Проверяем, что верификация выбрасывает ошибку
        with pytest.raises(ValueError, match="at least 1 year"):
            driver.verify()

    def test_driver_verify_success(self):
        """Тест успешной верификации водителя"""
        from app.models.domain.driver import Driver

        driver = Driver(user_id=1, license_number="TEST123", years_of_experience=2)
        driver.verify()
        assert driver.status == DriverStatus.VERIFIED


class TestDriverIntegration:
    """Интеграционные тесты работы с БД"""

    def test_create_driver_in_db(self, db):
        """Тест создания водителя в базе данных"""
        from app.services.driver_service import DriverService

        driver_data = DriverCreateRequest(
            user_id=100, license_number="INTEGRATION123", years_of_experience=4
        )

        driver = DriverService.create_driver(db, driver_data)

        assert driver.id is not None
        assert driver.license_number == "INTEGRATION123"
        assert driver.status == DriverStatus.PENDING

    def test_get_drivers_from_db(self, db):
        """Тест получения водителей из базы данных"""
        from app.services.driver_service import DriverService

        # Создаем несколько водителей
        driver1_data = DriverCreateRequest(
            user_id=101, license_number="DRIVER001", years_of_experience=2
        )

        driver2_data = DriverCreateRequest(
            user_id=102, license_number="DRIVER002", years_of_experience=5
        )

        DriverService.create_driver(db, driver1_data)
        DriverService.create_driver(db, driver2_data)

        # Получаем всех водителей
        drivers = DriverService.get_drivers(db)

        assert len(drivers) >= 2
        license_numbers = [driver.license_number for driver in drivers]
        assert "DRIVER001" in license_numbers
        assert "DRIVER002" in license_numbers


def test_health_check(client):
    """Тест health check эндпоинта"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_root_endpoint(client):
    """Тест корневого эндпоинта"""
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()
    assert "AutoPilot" in response.json()["message"]


def test_database_session():
    """Тест работы с сессией базы данных"""
    from app.database.session import get_db

    db_generator = get_db()
    db_session = next(db_generator)
    assert db_session is not None
    try:
        next(db_generator)
    except StopIteration:
        pass
