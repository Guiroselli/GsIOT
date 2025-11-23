from fastapi import FastAPI
from app.routers.analysis import router as analysis_router
from app.db.session import engine
from app.db.models import Base, Carreira
from sqlalchemy.orm import Session
from app.routers.career import router as career_router


# inicializa a aplicação FastAPI
app = FastAPI(title="CareerMap Python (SQLite local)", version="1.0")

# cria automaticamente o banco e as tabelas
Base.metadata.create_all(bind=engine)

# cria um seed inicial de carreiras (só na primeira vez)
with Session(engine) as s:
    if not s.query(Carreira).first():
        s.add_all([
            Carreira(nome="Data/ML", descricao="Ciência de Dados e Machine Learning"),
            Carreira(nome="Back-end", descricao="Serviços e APIs"),
            Carreira(nome="Front-end", descricao="Interfaces Web/Mobile"),
            Carreira(nome="Embarcados", descricao="IoT e Sistemas Embarcados"),
            Carreira(nome="DevOps", descricao="CI/CD e Cloud"),
            Carreira(nome="Full-Stack", descricao="Front + Back")
        ])
        s.commit()

@app.get("/health")
def health():
    return {"status": "ok"}

# inclui as rotas principais
app.include_router(analysis_router)
app.include_router(career_router)

