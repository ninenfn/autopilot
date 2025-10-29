import pytest
from app.models.schemas.driver import DriverCreateRequest
from app.models.domain.driver import DriverStatus

class TestDriversAPI:
    """Unit-тесты для API водителей"""
    
    def test_create_driver_success(self, client):
        """Тест успешного создания водителя"""
        driver_data = {
            "user_id": 1,
            "license_number": "AB123456",
            "years_of_experience": 5
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
            "years_of_experience": 3
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
            "years_of_experience": 60  # Too high
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
            "years_of_experience": 3
        }
        client.post("/drivers/", json=driver_data)
        
        # Получаем список
        response = client.get("/drivers/")
        
        assert response.status_code == 200
        drivers = response.json()
        assert len(drivers) == 1
        assert drivers[0]["license_number"] == "CD789012"
        assert drivers[0]["status"] == "PENDING"  # Теперь используем верхний регистр
    
    def test_get_drivers_with_filter(self, client):
        """Тест фильтрации водителей по статусу"""
        # Создаем тестового водителя
        driver_data = {
            "user_id": 3,
            "license_number": "EF345678",
            "years_of_experience": 7
        }
        client.post("/drivers/", json=driver_data)
        
        # Фильтруем по статусу PENDING (верхний регистр)
        response = client.get("/drivers/?status=PENDING")
        
        assert response.status_code == 200
        drivers = response.json()
        assert len(drivers) >= 1
        assert all(driver["status"] == "PENDING" for driver in drivers)

class TestDriverService:
    """Unit-тесты для сервиса водителей"""
    
    def test_driver_domain_logic(self):
        """Тест бизнес-логики domain модели"""
        from app.models.domain.driver import Driver
        
        driver = Driver(
            user_id=1,
            license_number="TEST123",
            years_of_experience=2
        )
        
        # Проверяем начальный статус
        assert driver.status == DriverStatus.PENDING
        
        # Тестируем верификацию
        driver.verify()
        assert driver.status == DriverStatus.VERIFIED
        
        # Тестируем отклонение
        driver.reject()
        assert driver.status == DriverStatus.REJECTED
    
    def test_driver_verification_validation(self):
        """Тест валидации при верификации"""
        from app.models.domain.driver import Driver
        
        driver = Driver(
            user_id=1,
            license_number="TEST123",
            years_of_experience=0  # Меньше 1 года
        )
        
        # Проверяем, что верификация выбрасывает ошибку
        try:
            driver.verify()
            assert False, "Should have raised ValueError"
        except ValueError as e:
            assert "at least 1 year" in str(e)

class TestDriverIntegration:
    """Интеграционные тесты работы с БД"""
    
    def test_create_driver_in_db(self, db):
        """Тест создания водителя в базе данных"""
        from app.services.driver_service import DriverService
        from app.models.schemas.driver import DriverCreateRequest
        
        driver_data = DriverCreateRequest(
            user_id=100,
            license_number="INTEGRATION123",
            years_of_experience=4
        )
        
        driver = DriverService.create_driver(db, driver_data)
        
        assert driver.id is not None
        assert driver.license_number == "INTEGRATION123"
        assert driver.status == DriverStatus.PENDING
    
    def test_get_drivers_from_db(self, db):
        """Тест получения водителей из базы данных"""
        from app.services.driver_service import DriverService
        from app.models.schemas.driver import DriverCreateRequest
        
        # Создаем несколько водителей
        driver1_data = DriverCreateRequest(
            user_id=101,
            license_number="DRIVER001",
            years_of_experience=2
        )
        
        driver2_data = DriverCreateRequest(
            user_id=102,
            license_number="DRIVER002", 
            years_of_experience=5
        )
        
        DriverService.create_driver(db, driver1_data)
        DriverService.create_driver(db, driver2_data)
        
        # Получаем всех водителей
        drivers = DriverService.get_drivers(db)
        
        assert len(drivers) >= 2
        license_numbers = [driver.license_number for driver in drivers]
        assert "DRIVER001" in license_numbers
        assert "DRIVER002" in license_numbers