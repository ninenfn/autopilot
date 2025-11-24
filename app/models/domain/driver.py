from enum import Enum

from pydantic import BaseModel


class DriverStatus(str, Enum):
    PENDING = "PENDING"
    VERIFIED = "VERIFIED"
    REJECTED = "REJECTED"


class Driver(BaseModel):
    """Domain model - содержит бизнес-логику и валидацию"""

    id: int | None = None  # Может быть None при создании
    user_id: int
    license_number: str
    years_of_experience: int
    status: DriverStatus = DriverStatus.PENDING

    def verify(self) -> None:
        """Business logic: верификация водителя"""
        if self.years_of_experience < 1:
            raise ValueError("Driver must have at least 1 year of experience")
        self.status = DriverStatus.VERIFIED

    def reject(self) -> None:
        """Business logic: отклонение водителя"""
        self.status = DriverStatus.REJECTED
