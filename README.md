# 🧭 CareerMap – API de Geração de Trilhas de Carreira com IA

Este projeto faz parte da entrega da disciplina **IoT & IA** da FIAP.  
O objetivo é construir uma **API inteligente** capaz de gerar **trilhas personalizadas de carreira**, com base em preferências do usuário.

A API utiliza:

- 🧠 **IA Generativa (Gemini)**
- 🔄 **Fallback automático** caso a IA esteja indisponível ou sem créditos
- 🗄️ **Banco SQLite** para armazenar trilhas geradas
- ⚡ **FastAPI** para servir endpoints rápidos e documentados
- 🐍 **Python 3.11+**

---

## 📚 Funcionalidades

### ✅ 1. Gerar trilha personalizada (`POST /api/gerar-trilha`)
A API recebe as preferências do usuário e gera um **plano de estudos completo**, contendo:

- carreira sugerida  
- justificativa  
- lista de módulos/etapas  
- carga horária total  
- ordem dos passos  

⚠️ Caso a IA da OpenAI falhe por falta de créditos ou indisponibilidade, a API usa um **plano base interno (fallback)**.

---

### ✅ 2. Salvar trilha no banco  
Toda trilha gerada é armazenada automaticamente em:

- tabela **trilha**
- tabela **curso** (passos)
- tabela **usuario** (associado pelo nome)

---

### ✅ 3. Buscar trilhas já geradas (`GET /api/trilhas/{usuario_nome}`)
Retorna todas as trilhas de um usuário já cadastrado no banco.

---

### ✅ 4. Documentação automática via Swagger
A API expõe sua documentação em:

👉 **http://localhost:8000/docs**

---

## 🛠️ Tecnologias Utilizadas

| Componente | Tecnologia |
|-----------|------------|
| Linguagem | Python 3.11 |
| Framework | FastAPI |
| IA Generativa | Gemini |
| Banco | SQLite |
| ORM | SQLAlchemy |
| Servidor | Uvicorn |
| Docs automáticas | Swagger (OpenAPI) |

---

## 📂 Estrutura do Projeto

```
CareerMap/
 ├── app/
 │   ├── db/
 │   │   ├── models.py
 │   │   └── session.py
 │   ├── routers/
 │   │   └── career.py
 │   ├── main.py
 │   └── ...
 ├── requirements.txt
 ├── schema_oracle.sql
 ├── .env
 └── README.md
```

---

## 🚀 Como Rodar o Projeto

### 1) Clone o repositório
```bash
git clone https://github.com/Guiroselli/GsIOT.git
cd CareerMap
```

---

### 2) Criar e ativar ambiente virtual

**Windows**
```bash
python -m venv .venv
.\.venv\Scripts\activate
```

---

### 3) Instalar dependências
```bash
pip install -r requirements.txt
```

---

### 4) Criar arquivo `.env`
```
OPENAI_API_KEY=sua_chave_aqui
```

---

### 5) Rodar o servidor
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

---

## 🔥 Endpoints Principais

### 🔹 POST /api/gerar-trilha
Body:
```json
{
  "nome": "Guilherme",
  "interesses": ["backend", "cloud", "IA"],
  "experiencia": "já fiz alguns projetos simples na faculdade",
  "prefere_areas": ["Backend", "DevOps"],
  "horas_por_semana": 8
}

```

---

### 🔹 GET /api/trilhas/{usuario_nome}

Exemplo:
```
GET /api/trilhas/Guilherme
```

---

## 🧠 IA Usada

A API tenta primeiro usar:

### 1️⃣ OpenAI GPT-4o-mini

Se a IA retornar erro 429 (sem créditos), é ativado o fallback:

### 2️⃣ Plano local baseado em regras internas

---

## 🗄️ Banco de Dados SQLite

Arquivo criado automaticamente:

```
careermap.db
```

Tabelas:

- usuario  
- trilha  
- curso  
- detalhe_deteccao *(não usada nesta versão)*  

---

## 👨‍💻 Autor

Projeto desenvolvido por:

**Guilherme** 
**Lucas Miranda**
**Gusthvao Daniel**

---|
