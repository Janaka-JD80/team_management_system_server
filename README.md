<div align="center">

### Team Management & AI Reporting Platform

Backend service powering secure Role-Based Access Control, immutable weekly reporting, and a Retrieval-Augmented Generation (RAG) AI Chat Assistant for team productivity analytics.

<p>
  <img alt="Python" src="https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white" />
  <img alt="FastAPI" src="https://img.shields.io/badge/FastAPI-0.100+-009688?style=for-the-badge&logo=fastapi&logoColor=white" />
  <img alt="PostgreSQL" src="https://img.shields.io/badge/PostgreSQL-15+-4169E1?style=for-the-badge&logo=postgresql&logoColor=white" />
  <img alt="SQLAlchemy" src="https://img.shields.io/badge/SQLAlchemy-2.0-D71F00?style=for-the-badge&logo=sqlalchemy&logoColor=white" />
  <img alt="ChromaDB" src="https://img.shields.io/badge/Vector_DB-ChromaDB-FF6F00?style=for-the-badge" />
</p>

<p>
  <img alt="Alembic" src="https://img.shields.io/badge/Migrations-Alembic-2C3E50?style=flat-square" />
  <img alt="AI" src="https://img.shields.io/badge/AI-Google_Gemini_%2B_Groq-010101?style=flat-square" />
  <img alt="JWT" src="https://img.shields.io/badge/Auth-JWT-000000?style=flat-square&logo=jsonwebtokens&logoColor=white" />
  <img alt="License" src="https://img.shields.io/badge/License-Proprietary-lightgrey?style=flat-square" />
</p>

</div>

---

## 📑 Table of Contents

- [✨ Features](#-features)
- [🧰 Tech Stack](#-tech-stack)
- [🏗️ Architecture](#️-architecture)
- [📂 Project Structure](#-project-structure)
- [🚀 Getting Started](#-getting-started)
  - [Prerequisites](#prerequisites)
  - [Configuration](#configuration)
  - [Installation](#installation)
  - [Running the API](#running-the-api)
- [🗄️ Database](#️-database)
- [🔌 API Overview](#-api-overview)
- [🔐 Authentication & RBAC](#-authentication--rbac)
- [🤖 AI Chat Assistant (RAG)](#-ai-chat-assistant-rag)
- [🧭 Development Notes](#-development-notes)

---

## ✨ Features

- 📝 **Weekly Reports** — Team members can submit, track, and edit their weekly tasks, blockers, and hours spent.
- 🛡️ **Immutable Audit Trail** — Manager corrections and team member edits never overwrite history; every edit spawns a new version row.
- 🧑‍💼 **Dynamic RBAC** — Granular, token-embedded permissions (e.g., `VIEW_DASHBOARD`, `MANAGE_USERS`) that can be reassigned without code deployments.
- 📊 **Team Analytics** — High-level managerial dashboard endpoints aggregating project hours and team productivity trends.
- 🤖 **AI Chat Assistant** — A built-in RAG pipeline allowing managers to query historical reports using natural language.
- 🔐 **Secure Auth** — JWT-based authentication issuing HTTP-only session cookies to mitigate XSS attacks.

---

## 🧰 Tech Stack

| Layer | Technology |
|-------|-----------|
| 🐍 Language | Python 3.10+ |
| ⚡ Framework | FastAPI |
| 🗃️ ORM | SQLAlchemy 2.0 (async) |
| 🐘 Database | PostgreSQL (`asyncpg`) |
| 🧬 Migrations | Alembic |
| 🧠 Vector DB | ChromaDB (Local) / PgVector (Prod) |
| 🤖 AI Models | Google Gemini (Embeddings) + Groq (Generation) |
| 🔑 Auth | PyJWT (HS256) |
| 🚀 Server | Uvicorn |

---

## 🏗️ Architecture

The application follows a clean, decoupled **N-Tier Enterprise Architecture** that separates concerns from HTTP entry down to persistence:

```text
Endpoints → Services → Repositories → Models (DB)
   (API)     (logic)     (queries)     (ORM)
```

- **Endpoints / Routes** — Define the REST surface and Pydantic request/response validation.
- **Services** — Encapsulate business logic, AI orchestration, and background tasks.
- **Repositories** — Own data access and query logic.
- **Models** — SQLAlchemy ORM entities mapped to PostgreSQL tables.
- **Integrations** — LLM Clients (Gemini/Groq) and Vector Database Factories.

---

## 📂 Project Structure

```text
app/
├── core/                  # App config, security, and exception handlers
├── main.py                # FastAPI app entry, middleware, CORS
├── api/v1/
│   ├── endpoints/         # Route handlers (auth, reports, ai_assistant...)
│   └── router.py          # Aggregated API router
├── db/
│   ├── base.py            # SQLAlchemy Base registry
│   └── session.py         # Async engine + AsyncSessionLocal factory
├── integrations/          # External API clients (LLM Client)
├── models/                # ORM models (users, reports, roles)
├── repositories/          # Data access layer
├── schemas/               # Pydantic validation schemas
├── services/              # Business logic (Report Review, RAG)
└── prompts/               # Isolated AI System Prompts
docs/
├── development/           # Architectural Decision Records (RAG Implementation)
└── runbooks/              # Operational flows and API cURL examples
migrations/                # Alembic migration files
run.py                     # Local development server runner
```

---

## 🚀 Getting Started

### Prerequisites

- 🐍 **Python 3.10+**
- 🐘 **PostgreSQL** running locally
- A database created for this project

### Configuration

Create a `.env` file in the project root using env.example:

```env
# Application
ENVIRONMENT=development

# Database
DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/tms_db

# JWT Security
SECRET_KEY=your-256-bit-secret
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30240

# LLM Providers (Required for RAG Assistant)
GEMINI_API_KEY=your_google_gemini_api_key
GROQ_API_KEY=your_groq_api_key

# CORS
CORS_ORIGINS=http://localhost:5173
```

> ⚠️ **Never commit secrets.** Keep `.env` out of version control.

### Installation

**Windows (PowerShell)**

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

**macOS / Linux**

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Running the API

```bash
python run.py
```

The service runs on 👉 **`http://localhost:5008`**

| Resource | URL |
|----------|-----|
| 📘 Swagger UI | `http://localhost:5008/docs` |
| 📗 ReDoc | `http://localhost:5008/redoc` |

---

## 🗄️ Database

### Migrations

Apply the latest schema migrations to build your Postgres tables:

```bash
alembic upgrade head
```

### Seeding

This project includes an idempotent seeder module to populate the local database with dummy data, initial roles, and statuses.

```bash
python -m app.db.run_seeders
```

<details>
<summary>📦 <strong>Seeded sample data & Test Credentials</strong></summary>

- **Permissions & Roles:** `ADMIN`, `MANAGER`, `TEAM_MEMBER`
- **Statuses:** `DRAFT`, `SUBMITTED`, `NEEDS_CORRECTION`, `APPROVED`
- **Projects & Reports:** Sample projects and historic weekly reports

**Test Credentials (Password for all is `password123`)**
- 🛡️ **Admin:** `admin@example.com`
- 🧑‍💼 **Manager:** `manager1@example.com` (up to `manager3`)
- 📝 **Team Member:** `member1@example.com` (up to `member10`)
</details>

*(Note: The Vector Database collections will auto-initialize via the `ChromaDB` client upon startup).*

---

## 🔌 API Overview

All routes are served under the `/api/v1` prefix.

| Prefix | Tag | Description |
|--------|-----|-------------|
| `/auth` | 🔐 auth | Registration, Login, HTTP-only Cookie issuance |
| `/users` | 👤 users | Profile management |
| `/roles` | 🛡️ roles | RBAC role definitions (Admin only) |
| `/permissions` | 🔑 permissions | Granular access control mapping |
| `/projects` | 📁 projects | Project definitions |
| `/reports` | 📝 reports | Weekly report submissions & manager reviews |
| `/analytics` | 📊 analytics | Team Dashboard aggregations |
| `/ai-assistant` | 🤖 ai-assistant | Natural language RAG querying |

---

## 🔐 Authentication & RBAC

Authentication utilizes stateless JWTs stored in `HTTP-Only` cookies to prevent XSS data extraction.

1. `POST /api/v1/auth/login` — Verifies credentials.
2. The server serializes the user's granular **Permissions** (e.g., `["VIEW_DASHBOARD", "CREATE_REPORT"]`) directly into the JWT Payload.
3. Protected routes utilize the `RequirePermission` FastAPI dependency to authorize actions instantly without querying the database.

See [docs/runbooks/rbac-service.md](./docs/runbooks/rbac-service.md) for the exact API flows.

---

## 🤖 AI Chat Assistant (RAG)

The backend features a **Retrieval-Augmented Generation** pipeline that allows managers to chat with their data.

- **Background Sync:** Upon report approval, the service utilizes **Google Gemini** to generate a 768-dimensional embedding of the report text.
- **Factory Pattern Vector DB:** Embeddings are saved to **ChromaDB** on local Windows/Mac environments, or **PgVector** in AWS Production environments.
- **Inference:** When queried, the system uses L2 Euclidean Distance to retrieve the top 5 reports and passes them to a high-speed **Groq Llama** model.
- **Privacy:** Vector searches are strictly protected at the endpoint layer via the `RequireRole("MANAGER")` dependency.

See [docs/development/rag-implementation.md](./docs/development/rag-implementation.md) for architectural insights.

---

## 🧭 Development Notes

- 🧬 Keep Alembic migrations **schema-only**.
- 🧱 Follow the layered flow: **Endpoint → Service → Repository → Model**.
- ⏱️ Ensure synchronous SDK calls (like `google-genai` or `groq`) are strictly wrapped in `asyncio.to_thread()` inside the service layer to prevent FastAPI event loop freezing.

---

<div align="center">

Made with ❤️ for better team productivity · **Sisenco Digital**

</div>
