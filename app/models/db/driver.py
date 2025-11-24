import enum

from sqlalchemy import Column, Enum, Integer, String

from app.database.session import Base


class DriverStatusDB(enum.Enum):
    PENDING = "PENDING"
    VERIFIED = "VERIFIED"
    REJECTED = "REJECTED"


class DriverDB(Base):
    __tablename__ = "drivers"

    id: Column[int] = Column(Integer, primary_key=True, index=True)
    user_id: Column[int] = Column(Integer, nullable=False)
    license_number: Column[str] = Column(String, unique=True, index=True)
    years_of_experience: Column[int] = Column(Integer, nullable=False)
    status: Column[DriverStatusDB] = Column(Enum(DriverStatusDB), default=DriverStatusDB.PENDING)
