# RAG Implementation & Development Guide

## 1. Architectural Approach
The Retrieval-Augmented Generation (RAG) pipeline is designed to augment standard LLM knowledge with  proprietary Weekly Report data. 

**Design Decisions:**
- **Decoupled LLMs:** We utilized Google Gemini specifically for its industry-leading Embedding Models (converting text into 768-dimensional mathematical arrays). We utilized Groq (Llama models) for the final chat generation due to its ultra-low latency streaming speeds.
- **Vector Storage Strategy:** We implemented the **Factory Design Pattern** with an Abstract Base Class (`BaseVectorStore`).
  - **Local Development:** Uses `ChromaDB`, a lightweight file-based vector store that saves data to a local `/chroma_data` directory. This allows developers on Windows/Mac to pull the repository and run it instantly without compiling C++ Postgres extensions.
  - **Production Deployment:** Seamlessly swaps to `pgvector`, a native PostgreSQL extension, to maintain high availability in Linux environments.

## 2. System Prompt Design
The System Prompt is isolated in `app/prompts/ai_prompts.py` to maintain the Single Responsibility Principle within the Service layer.

**Prompt Engineering Tactics Used:**
- **Strict Bounding:** The prompt explicitly states: *"Do not invent information. If the answer is not in the context, say 'I don't have enough data'."* This effectively mitigates hallucination.
- **Markdown Enforcement:** The prompt includes a `CRITICAL FORMATTING RULES` block, aggressively commanding the LLM to use bullet points, bolding, and hard newlines inside tables. This guarantees the Frontend React Markdown parser can render it beautifully.

## 3. Data Privacy & Security Considerations
Data privacy in a corporate environment is critical. We cannot allow standard Team Members to query the AI and accidentally retrieve a Manager's confidential reports or analytics.

**Implementation:**
- **Endpoint-Level Authorization:** Instead of complex metadata filtering at the database level, we rely on strict Role-Based Access Control (RBAC) at the API Gateway level.
- **Role Requirement:** The `/api/v1/ai-assistant/chat` endpoint is strictly protected by the `RequireRole("MANAGER")` (or equivalent permission) dependency in FastAPI. 
- **Result:** If a standard Team Member attempts to access the AI Chat, the request is instantly rejected with a `403 Forbidden` error before it ever reaches the Vector Database or the LLM. This guarantees that only authorized managers can query the centralized report knowledge base.
