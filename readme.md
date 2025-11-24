# AutoPilot API - Quality Assurance Report

## Покрытие тестами: 100%

### Статистика покрытия по модулям

| Модуль                         | Покрытие |
|--------------------------------|----------|
| app/api/drivers.py             |   100%   |
| app/services/driver_service.py |   100%   |
| app/database/session.py        |   100%   |
| app/models/domain/driver.py    |   100%   |
| app/models/db/driver.py        |   100%   |
| app/models/schemas/driver.py   |   100%   |
| **Общее покрытие**             | **100%** |

### Команды для запуска тестов:

```bash
# Установка зависимостей
pip install pytest pytest-cov allure-pytest

# Запуск тестов с покрытием
pytest
или
pytest --cov=app --cov-report=term-missing

# HTML отчет покрытия
pytest --cov=app --cov-report=html

# Allure отчеты
pytest --alluredir=allure-results
allure serve allure-results
```
![Покрытие](https://s3.iimg.su/s/21/grBHjMUxCAWWrolLfc9bOdbJq3C1f6nVEhrEmB2t.png)

## Конфигурации линтеров и форматеров

Ключевые особенности конфигурации:

** Все инструменты используют line-length=100

** Python 3.11+ с строгой типизацией

** Игнорирование специфичных для проекта ошибок

** Ruff и Black могут автофиксить большинство проблем

### Настройки в `pyproject.toml`:

####  **Black** (автоформатирование)
```toml
[tool.black]
line-length = 100                    # Максимальная длина строки
target-version = ['py311']          # Целевая версия Python
include = '\.pyi?$'                 # Форматировать .py и .pyi файлы
```

####  Ruff (линтинг и автофикс)
```toml
[tool.ruff]
line-length = 100
target-version = "py311"
[tool.ruff.lint]
select = ["E", "W", "F", "I", "B", "C4", "UP"]  # Проверяемые правила
ignore = ["E501", "B008", "C901", "B904", "F821"]  # Игнорируемые правила
```

####   Isort (сортировка импортов)
```toml
[tool.isort]
profile = "black"           # Совместимость с Black
line_length = 100          # Длина строки
multi_line_output = 3      # Стиль многострочных импортов
```

####   MyPy (статическая типизация)
```toml
[tool.mypy]
python_version = "3.10"
disallow_untyped_defs = true    # Запрет нетипизированных функций
no_implicit_optional = true     # Явные Optional типы
warn_unused_ignores = true      # Предупреждения о неиспользуемых ignore

# Исключения для тестов и SQLAlchemy
[[tool.mypy.overrides]]
module = "tests.*"
disallow_untyped_defs = false

[[tool.mypy.overrides]]
module = ["app.models.db.*", "sqlalchemy.*", "alembic.*"]
disallow_subclassing_any = false
```

## Пример запуска pre-commit
![pre-commit](https://s3.iimg.su/s/21/gh5v1XJxRuOc2qpXr0rJkrJJytBDh92UqkTPWRUH.png)

## Вывод mypy

```bash
mypy app tests
```
![mypy](https://s3.iimg.su/s/21/gt0RbtqxTJe8EBrEPPmDYjYrvGleaYNTUWzDoddh.png)
