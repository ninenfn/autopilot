from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List, Optional

from app.database.session import get_db
from app.models.schemas.driver import DriverCreateRequest, DriverResponse
from app.models.domain.driver import DriverStatus
from app.services.driver_service import DriverService

router = APIRouter(prefix="/drivers", tags=["drivers"])

@router.post(
    "/", 
    response_model=DriverResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Создать профиль водителя"
)
async def create_driver(
    driver_data: DriverCreateRequest,
    db: Session = Depends(get_db)
):
    """
    Создание нового профиля водителя.
    
    - **user_id**: ID пользователя в системе
    - **license_number**: Номер водительского удостоверения
    - **years_of_experience**: Опыт вождения в годах
    """
    try:
        driver = DriverService.create_driver(db, driver_data)
        return driver
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Driver with this license number already exists"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )

@router.get(
    "/",
    response_model=List[DriverResponse],
    summary="Получить список водителей"
)
async def get_drivers(
    status: Optional[DriverStatus] = Query(None, description="Фильтр по статусу верификации"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """
    Получение списка водителей с возможностью фильтрации по статусу.
    
    - **status**: Статус верификации (PENDING, VERIFIED, REJECTED)
    - **skip**: Количество записей для пропуска (пагинация)
    - **limit**: Максимальное количество записей
    """
    try:
        drivers = DriverService.get_drivers(db, status, skip, limit)
        return drivers
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )
        
