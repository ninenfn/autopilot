from pydantic import BaseModel, Field, ConfigDict  # Добавляем ConfigDict
from typing import Optional
from app.models.domain.driver import DriverStatus

# Схемы для запросов (Request)
class DriverCreateRequest(BaseModel):
    user_id: int = Field(gt=0, description="User ID must be positive")
    license_number: str = Field(min_length=5, max_length=20)
    years_of_experience: int = Field(ge=0, le=50, description="Experience must be between 0 and 50 years")

class DriverUpdateRequest(BaseModel):
    status: DriverStatus

# Схемы для ответов (Response)  
class DriverResponse(BaseModel):
    id: int
    user_id: int
    license_number: str
    years_of_experience: int
    status: DriverStatus
    
    model_config = ConfigDict(from_attributes=True)