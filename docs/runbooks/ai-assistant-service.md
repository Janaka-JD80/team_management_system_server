# AI Assistant & RAG Runbook

## 1. Executive Summary & Purpose
This document outlines the architecture and operational flow of the **Retrieval-Augmented Generation (RAG)** Chat Assistant. The Assistant empowers managers and team members to instantly query historical report data using natural language.

---

## 2. Architecture Overview

The RAG pipeline utilizes a **Hybrid Database Strategy**:
1. **Vector Database:** Stores 768-dimensional mathematical embeddings of the text. Uses a Factory Pattern to dynamically boot `ChromaDB` locally and `pgvector` in production.
2. **LLM Orchestration:** `google-genai` is used to generate embeddings. `Groq` is used to power the high-speed Llama conversational models.

### RAG Data Flow (Exact Flow)

**Step 1: User Query**
- A user submits a natural language question (e.g., "What did Jane do?") on the web client.
- The client sends a `POST /api/v1/ai-assistant/chat` request to the backend.

**Step 2: Semantic Embedding**
- The backend sends the text query to the `Google Gemini` API.
- Gemini converts the text into a 768-dimensional mathematical embedding and returns it to the backend.

**Step 3: Vector Search (L2 Distance)**
- The backend queries the Vector Database (either `ChromaDB` or `PgVector`).
- The Vector DB calculates the L2 Euclidean Distance against all stored report vectors and returns the top 5 most mathematically similar historical reports.

**Step 4: LLM Generation**
- The backend constructs a strict System Prompt containing the formatting rules and injects the 5 retrieved reports as the Context Block.
- The backend streams the System Prompt and User Query to the `Groq` API (using a high-speed Llama model).
- Groq processes the context, generates a Markdown-formatted response, and returns it to the user.

---

## 3. Operational Workflow & API Usage

### 3.1. Query the AI Assistant
Sends a natural language query to the RAG pipeline.

**Request:**
```bash
curl -X POST "http://localhost:8000/api/v1/ai-assistant/chat" \
     -H "Content-Type: application/json" \
     -H "Cookie: access_token=..." \
     -d '{"message": "Summarize the major blockers from last week"}'
```

**Expected Response (200 OK):**
```json
{
  "status": "success",
  "message": "Chat generated",
  "data": {
    "response": "### Major Blockers\n- Database latency issues\n- Deployment pipeline failure"
  }
}
```

---

## 4. Security & Maintenance Guardrails

- **Event Loop Blocking:** The official SDKs for Groq and Google GenAI are synchronous. They MUST be wrapped in `asyncio.to_thread` to prevent freezing the FastAPI event loop during API calls.
- **Data Privacy (Endpoint Authorization):** The `/api/v1/ai-assistant/chat` endpoint is strictly protected by RBAC. Only users with Manager or Admin roles can query the AI, instantly preventing standard team members from accessing global report data via a `403 Forbidden`.
- **Hallucination Prevention:** The System Prompt strictly commands the LLM to refuse answering if the Vector DB returns no relevant chunks.

### Error Remediation Codes
| Status Code | Message | Cause & Remediation |
|-------------|---------|---------------------|
| `500` | LLM Client not configured | Missing API keys in the `.env` file. |
| `500` | Failed to generate embedding | Google GenAI outage or rate limit. Implement exponential backoff. |
