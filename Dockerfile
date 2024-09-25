# Стартовое изображение Python
FROM python:3.9-slim

# Установка зависимостей
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копирование исходного кода приложения
COPY . .

# Установка FastAPI и другие зависимости
RUN pip install fastapi uvicorn sqlmodel redis pyjwt

# Выполение команды для создания таблиц в PostgreSQL
RUN python -c "from sqlmodel import SQLModel, Session, Engine; from sqlalchemy import create_engine; engine = create_engine('postgresql://user:password@localhost/database'); SQLModel.metadata.create_all(engine)"

# Установка зависимостей slowapi
RUN pip install slowapi

# Создание образа Docker
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
