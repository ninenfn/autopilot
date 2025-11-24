import logging

from sqlalchemy.orm import Session

from app.models.db.driver import DriverDB, DriverStatusDB
from app.models.domain.driver import Driver, DriverStatus
from app.models.schemas.driver import DriverCreateRequest

logger = logging.getLogger(__name__)


class DriverService:
    @staticmethod
    def create_driver(db: Session, driver_data: DriverCreateRequest) -> Driver:
        """Создание водителя с конвертацией между слоями"""
        try:
            # Проверяем, нет ли уже водителя с таким номером прав
            existing_driver = (
                db.query(DriverDB)
                .filter(DriverDB.license_number == driver_data.license_number)
                .first()
            )

            if existing_driver:
                raise ValueError(
                    f"Driver with license number {driver_data.license_number} already exists"
                )

            # Pydantic -> Domain
            domain_driver = Driver(
                user_id=driver_data.user_id,
                license_number=driver_data.license_number,
                years_of_experience=driver_data.years_of_experience,
            )

            # Domain -> DB (конвертируем статус)
            db_driver = DriverDB(
                user_id=domain_driver.user_id,
                license_number=domain_driver.license_number,
                years_of_experience=domain_driver.years_of_experience,
                status=DriverStatusDB[domain_driver.status.value],  # Конвертируем правильно
            )

            db.add(db_driver)
            db.commit()
            db.refresh(db_driver)

            # DB -> Domain
            return DriverService._db_to_domain(db_driver)

        except Exception as e:
            db.rollback()
            logger.error(f"Error creating driver: {str(e)}")
            raise

    @staticmethod
    def get_drivers(
        db: Session,
        status: DriverStatus | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Driver]:
        """Получение списка водителей с фильтрацией"""
        try:
            query = db.query(DriverDB)

            if status:
                # Конвертируем Pydantic enum в SQLAlchemy enum
                db_status = DriverStatusDB[status.value]
                query = query.filter(DriverDB.status == db_status)

            db_drivers = query.offset(skip).limit(limit).all()

            # DB -> Domain конвертация
            return [DriverService._db_to_domain(driver) for driver in db_drivers]

        except Exception as e:
            logger.error(f"Error getting drivers: {str(e)}")
            raise

    @staticmethod
    def _db_to_domain(db_driver: DriverDB) -> Driver:
        """Конвертация DB модели в Domain модель"""
        return Driver(
            id=db_driver.id,  # type: ignore
            user_id=db_driver.user_id,  # type: ignore
            license_number=db_driver.license_number,  # type: ignore
            years_of_experience=db_driver.years_of_experience,  # type: ignore
            status=DriverStatus(db_driver.status.value),
        )


# тут можно добавить метрики логирование
# metrics.counter('drivers_created_total').inc()
# metrics.histogram('driver_creation_duration_seconds').observe(duration)
# Логи: создание/получение водителей, ошибки валидации
# Метрики: количество созданных водителей, время выполнения операций
# logger.info(f"Driver created: {driver_data.license_number}")
# metrics.counter('drivers_created').inc()
