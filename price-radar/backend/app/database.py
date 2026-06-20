import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Адрес подключения берет параметры из настроек docker-compose.yml
# Имя хоста 'db' совпадает с именем контейнера БД в сети Docker
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@db:5432/pricedb")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Генератор сессий для инъекции зависимостей FastAPI
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
