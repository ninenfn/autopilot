from sqlalchemy import Column, Integer, String, Enum
from app.database.session import Base
import enum

class DriverStatusDB(enum.Enum):
    PENDING = "PENDING"  
    VERIFIED = "VERIFIED"
    REJECTED = "REJECTED"

class DriverDB(Base):
    __tablename__ = "drivers"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)
    license_number = Column(String, unique=True, index=True)
    years_of_experience = Column(Integer, nullable=False)
    status = Column(Enum(DriverStatusDB), default=DriverStatusDB.PENDING)