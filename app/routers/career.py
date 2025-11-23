import os
import json
import logging
from typing import List, Dict, Optional

from google import genai
from fastapi import APIRouter
from pydantic import BaseModel
from dotenv import load_dotenv
from sqlalchemy.orm import Session



from app.db.session import SessionLocal
from app.db import models as m

load_dotenv()

GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
router = APIRouter(prefix="/api", tags=["career"])


# -----------------------------
# MODELOS DE ENTRADA E SAÍDA
# -----------------------------

class PreferenciasUsuario(BaseModel):
    nome: str
    interesses: List[str]
    experiencia: str
    prefere_areas: List[str]
    horas_por_semana: int


class TrilhaItemOut(BaseModel):
    ordem: int
    titulo: str
    descricao: str
    carga_horaria: Optional[int] = None


class TrilhaOut(BaseModel):
    trilha_id: int
    carreira: str
    justificativa: str
    passos: List[TrilhaItemOut]


class CareerResponse(BaseModel):
    usuario: str
    trilhas: List[TrilhaOut]


# -----------------------------
# IA SIMULADA (SEM OPENAI)
# -----------------------------

from openai import OpenAI  # coloque isso junto dos outros imports no topo


def gerar_trilha_com_ia(prefs: PreferenciasUsuario, carreiras_disponiveis: List[str]) -> Dict:
    """
    Versão com IA real (Gemini) + fallback seguro.

    Se der qualquer erro na chamada da API, volta para um plano padrão fixo.
    """

    def plano_fallback(motivo: str) -> Dict:
        carreira_fb = prefs.prefere_areas[0] if prefs.prefere_areas else carreiras_disponiveis[0]
        logging.warning(f"Usando plano fallback da IA. Motivo: {motivo}")
        return {
            "carreira": carreira_fb,
            "justificativa": f"Carreira escolhida com base nas áreas preferidas (fallback: {motivo}).",
            "passos": [
                {
                    "ordem": 1,
                    "titulo": "Fundamentos de Programação com Python",
                    "descricao": "Aprender lógica, variáveis, estruturas de controle e funções usando Python.",
                    "carga_horaria": 20,
                },
                {
                    "ordem": 2,
                    "titulo": "Git e Versionamento de Código",
                    "descricao": "Uso básico de Git, commits, branches e trabalho colaborativo com GitHub.",
                    "carga_horaria": 10,
                },
                {
                    "ordem": 3,
                    "titulo": f"Introdução à área de {carreira_fb}",
                    "descricao": f"Conceitos principais da área de {carreira_fb}, ferramentas e boas práticas.",
                    "carga_horaria": 25,
                },
            ],
        }

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return plano_fallback("GEMINI_API_KEY não configurada")

    try:
        # Cliente Gemini (google-genai)
        client = genai.Client(api_key=api_key)

        lista_carreiras = ", ".join(carreiras_disponiveis)

        prompt_sistema = (
            "Você é uma IA especializada em educação e carreira em tecnologia. "
            "Monte trilhas de estudo práticas e organizadas, pensando em alunos de graduação. "
            "Retorne APENAS um JSON válido, sem texto extra, sem markdown."
        )

        prompt_usuario = f"""
Perfil do usuário:
- Nome: {prefs.nome}
- Interesses: {", ".join(prefs.interesses)}
- Experiência: {prefs.experiencia}
- Áreas preferidas: {", ".join(prefs.prefere_areas)}
- Horas disponíveis por semana: {prefs.horas_por_semana}

Carreiras disponíveis: {lista_carreiras}

Monte um plano no formato JSON exato:

{{
  "carreira": "NOME_DA_CARREIRA_ESCOLHIDA (uma das disponíveis)",
  "justificativa": "texto explicando o porquê dessa carreira",
  "passos": [
    {{
      "ordem": 1,
      "titulo": "Nome do primeiro passo",
      "descricao": "Descrição do que estudar/fazer",
      "carga_horaria": 10
    }},
    {{
      "ordem": 2,
      "titulo": "Nome do segundo passo",
      "descricao": "Descrição do que estudar/fazer",
      "carga_horaria": 12
    }}
  ]
}}

Lembre-se: responda SOMENTE com o JSON.
"""

        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=[
                {"role": "user", "parts": [{"text": prompt_sistema}]},
                {"role": "user", "parts": [{"text": prompt_usuario}]},
            ],
        )

        raw_text = response.text  # texto retornado pelo Gemini
        plano = json.loads(raw_text)  # tenta interpretar como JSON

        carreira = plano.get("carreira") or (prefs.prefere_areas[0] if prefs.prefere_areas else carreiras_disponiveis[0])
        justificativa = plano.get("justificativa") or "Carreira sugerida pela IA com base no perfil informado."
        passos = plano.get("passos") or []

        passos_normalizados = []
        for i, p in enumerate(passos, start=1):
            passos_normalizados.append(
                {
                    "ordem": p.get("ordem") or i,
                    "titulo": p.get("titulo") or f"Passo {i}",
                    "descricao": p.get("descricao") or "",
                    "carga_horaria": int(p.get("carga_horaria") or 10),
                }
            )

        return {
            "carreira": carreira,
            "justificativa": justificativa,
            "passos": passos_normalizados,
        }

    except json.JSONDecodeError:
        # Caso o modelo não retorne JSON certinho
        logging.exception("JSON inválido retornado pela IA Gemini")
        return plano_fallback("JSON inválido retornado pela IA Gemini")

    except Exception as e:
        logging.exception(f"Erro ao chamar Gemini: {e}")
        return plano_fallback(f"erro na chamada da API Gemini: {e.__class__.__name__}")





# -----------------------------
# ROTA PRINCIPAL: GERAR TRILHA
# -----------------------------

@router.post("/gerar-trilha", response_model=CareerResponse)
def gerar_trilha(preferencias: PreferenciasUsuario):
    db: Session = SessionLocal()
    try:
        # Carreiras existentes
        carreiras = db.query(m.Carreira).all()
        nomes_carreiras = [c.nome for c in carreiras]

        plano = gerar_trilha_com_ia(preferencias, nomes_carreiras)

        carreira_nome = plano["carreira"]
        justificativa = plano["justificativa"]
        passos = plano["passos"]

        carreira_obj = next((c for c in carreiras if c.nome == carreira_nome), None)

        # Fallback de carreira (NUNCA pode ser None)
        if carreira_obj is None and carreiras:
            carreira_obj = carreiras[0]

        # ---- garante usuário ----
        usuario = (
            db.query(m.Usuario)
            .filter(m.Usuario.nome == preferencias.nome)
            .first()
        )

        if usuario is None:
            email_fake = f"{preferencias.nome.lower().replace(' ', '')}@example.com"
            usuario = m.Usuario(nome=preferencias.nome, email=email_fake)
            db.add(usuario)
            db.commit()
            db.refresh(usuario)

        # ---- cria trilha ----
        trilha = m.Trilha(
            usuario_id=usuario.id,
            carreira_id=carreira_obj.id,
            score_total=None,
        )
        db.add(trilha)
        db.commit()
        db.refresh(trilha)

        trilha_id = trilha.id  # guarda antes de fechar a sessão

        trilha_items_out: List[TrilhaItemOut] = []

        # ---- cria cursos e itens da trilha ----
        for p in passos:
            curso = m.Curso(
                titulo=p["titulo"],
                provedor="IA",
                carga_horaria=p["carga_horaria"],
            )
            db.add(curso)
            db.commit()
            db.refresh(curso)

            item = m.TrilhaItem(
                trilha_id=trilha_id,
                curso_id=curso.id,
                ordem=p["ordem"],
            )
            db.add(item)
            db.commit()

            trilha_items_out.append(
                TrilhaItemOut(
                    ordem=p["ordem"],
                    titulo=p["titulo"],
                    descricao=p["descricao"],
                    carga_horaria=p["carga_horaria"],
                )
            )

        # resposta
        return CareerResponse(
            usuario=preferencias.nome,
            trilhas=[
                TrilhaOut(
                    trilha_id=trilha_id,
                    carreira=carreira_obj.nome,
                    justificativa=justificativa,
                    passos=sorted(trilha_items_out, key=lambda x: x.ordem),
                )
            ],
        )
    finally:
        db.close()


# -----------------------------
# ROTA EXTRA: LISTAR TRILHAS
# -----------------------------

@router.get("/trilhas/{usuario_nome}", response_model=CareerResponse)
def listar_trilhas(usuario_nome: str):
    db: Session = SessionLocal()
    try:
        usuario = (
            db.query(m.Usuario)
            .filter(m.Usuario.nome == usuario_nome)
            .first()
        )

        if not usuario:
            return {"usuario": usuario_nome, "trilhas": []}

        trilhas = (
            db.query(m.Trilha)
            .filter(m.Trilha.usuario_id == usuario.id)
            .all()
        )

        trilhas_out = []

        for t in trilhas:
            carreira = db.query(m.Carreira).filter(m.Carreira.id == t.carreira_id).first()

            itens = (
                db.query(m.TrilhaItem)
                .filter(m.TrilhaItem.trilha_id == t.id)
                .order_by(m.TrilhaItem.ordem)
                .all()
            )

            passos = []
            for item in itens:
                curso = db.query(m.Curso).filter(m.Curso.id == item.curso_id).first()
                passos.append({
                    "ordem": item.ordem,
                    "titulo": curso.titulo,
                    "descricao": curso.titulo,
                    "carga_horaria": curso.carga_horaria,
                })

            trilhas_out.append({
                "trilha_id": t.id,
                "carreira": carreira.nome if carreira else "Desconhecida",
                "justificativa": "Trilha previamente gerada",
                "passos": passos
            })

        return {
            "usuario": usuario_nome,
            "trilhas": trilhas_out
        }
    finally:
        db.close()
