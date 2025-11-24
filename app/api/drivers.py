from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi import status as http_status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models.domain.driver import DriverStatus
from app.models.schemas.driver import DriverCreateRequest, DriverResponse
from app.services.driver_service import DriverService

router = APIRouter(prefix="/drivers", tags=["drivers"])


@router.post(
    "/",
    response_model=DriverResponse,
    status_code=http_status.HTTP_201_CREATED,
    summary="Создать профиль водителя",
)
async def create_driver(
    driver_data: DriverCreateRequest, db: Session = Depends(get_db)
) -> DriverResponse:
    """
    Создание нового профиля водителя.

    - **user_id**: ID пользователя в системе
    - **license_number**: Номер водительского удостоверения
    - **years_of_experience**: Опыт вождения в годах
    """
    try:
        # В create_driver после создания driver:
        driver = DriverService.create_driver(db, driver_data)
        if driver.id is None:
            raise HTTPException(
                status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Driver ID is missing",
            )
        return DriverResponse(
            id=driver.id,  # Теперь точно int
            user_id=driver.user_id,
            license_number=driver.license_number,
            years_of_experience=driver.years_of_experience,
            status=driver.status,
        )
    except ValueError as e:
        raise HTTPException(status_code=http_status.HTTP_400_BAD_REQUEST, detail=str(e)) from None
    except IntegrityError:
        raise HTTPException(
            status_code=http_status.HTTP_409_CONFLICT,
            detail="Driver with this license number already exists",
        ) from None
    except Exception as e:
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}",
        ) from None


@router.get("/", response_model=list[DriverResponse], summary="Получить список водителей")
async def get_drivers(
    status: DriverStatus | None = Query(None),
    skip: int = Query(0),
    limit: int = Query(100),
    db: Session = Depends(get_db),
) -> list[DriverResponse]:
    """
    Получение списка водителей с возможностью фильтрации по статусу.

    - **status**: Статус верификации (PENDING, VERIFIED, REJECTED)
    - **skip**: Количество записей для пропуска (пагинация)
    - **limit**: Максимальное количество записей
    """
    try:
        drivers = DriverService.get_drivers(db, status, skip, limit)
        # Конвертируем список Driver в список DriverResponse
        return [
            DriverResponse(
                id=driver.id if driver.id is not None else 0,  # Запасной вариант
                user_id=driver.user_id,
                license_number=driver.license_number,
                years_of_experience=driver.years_of_experience,
                status=driver.status,
            )
            for driver in drivers
        ]
    except Exception as e:
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}",
        ) from None
