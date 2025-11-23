import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# caminho do banco local (vai gerar o arquivo careermap.db na raiz)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
DB_PATH = os.path.join(BASE_DIR, "careermap.db")

DB_URL = f"sqlite:///{DB_PATH}"

engine = create_engine(DB_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
