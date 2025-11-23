# app/db/models.py
from __future__ import annotations
from datetime import datetime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import String, Integer, Float, DateTime, ForeignKey, func

# Base declarativa
class Base(DeclarativeBase):
    pass

# ---------- Tabelas principais ----------
class Usuario(Base):
    __tablename__ = "usuario"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    nome: Mapped[str | None] = mapped_column(String(200))
    email: Mapped[str | None] = mapped_column(String(200), unique=True)

class Carreira(Base):
    __tablename__ = "carreira"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    nome: Mapped[str] = mapped_column(String(200))
    descricao: Mapped[str | None] = mapped_column(String(1000))

class Curso(Base):
    __tablename__ = "curso"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    titulo: Mapped[str] = mapped_column(String(300))
    provedor: Mapped[str | None] = mapped_column(String(120))
    carga_horaria: Mapped[int | None] = mapped_column(Integer)

class PesoClasseCarreira(Base):
    __tablename__ = "peso_classe_carreira"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    classe_yolo: Mapped[str] = mapped_column(String(120))
    carreira_id: Mapped[int] = mapped_column(Integer, ForeignKey("carreira.id"))
    peso: Mapped[float] = mapped_column(Float)

# ---------- Detecção ----------
class Deteccao(Base):
    __tablename__ = "deteccao"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    usuario_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("usuario.id"))
    criado_em: Mapped[datetime] = mapped_column(
    DateTime(timezone=True),
    server_default=func.current_timestamp()
)


class DetalheDeteccao(Base):
    __tablename__ = "detalhe_deteccao"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    deteccao_id: Mapped[int] = mapped_column(Integer, ForeignKey("deteccao.id"))
    label: Mapped[str] = mapped_column(String(120))
    confidence: Mapped[float] = mapped_column(Float)
    x: Mapped[float | None] = mapped_column(Float)
    y: Mapped[float | None] = mapped_column(Float)
    w: Mapped[float | None] = mapped_column(Float)
    h: Mapped[float | None] = mapped_column(Float)

# ---------- Trilha ----------
class Trilha(Base):
    __tablename__ = "trilha"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    usuario_id: Mapped[int] = mapped_column(Integer, ForeignKey("usuario.id"))
    carreira_id: Mapped[int] = mapped_column(Integer, ForeignKey("carreira.id"))
    score_total: Mapped[float | None] = mapped_column(Float)
    criado_em: Mapped[datetime] = mapped_column(
    DateTime(timezone=True),
    server_default=func.current_timestamp()
)


class TrilhaItem(Base):
    __tablename__ = "trilha_item"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    trilha_id: Mapped[int] = mapped_column(Integer, ForeignKey("trilha.id"))
    curso_id: Mapped[int] = mapped_column(Integer, ForeignKey("curso.id"))
    ordem: Mapped[int | None] = mapped_column(Integer)
