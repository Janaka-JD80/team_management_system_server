from pathlib import Path
from typing import List, Dict, Any, Optional
from abc import ABC, abstractmethod
from app.core.config import settings
import chromadb
from sqlalchemy import text
from app.db.session import async_session


class BaseVectorStore(ABC):
    
    @abstractmethod
    async def upsert(self, doc_id: str, text: str, embedding: List[float]):
        pass
        
    @abstractmethod
    async def search(self, embedding: List[float], limit: int = 5) -> List[Dict[str, Any]]:
        pass


class ChromaVectorStore(BaseVectorStore):
    def __init__(self):
        db_path = Path(__file__).resolve().parents[2] / "chroma_data"
        self.client = chromadb.PersistentClient(path=db_path)
        self.collection = self.client.get_or_create_collection(name="reports")
        
    async def upsert(self, doc_id: str, text: str, embedding: List[float]):
        self.collection.upsert(
            ids=[doc_id],
            documents=[text],
            embeddings=[embedding],
        )
        
    async def search(self, embedding: List[float], limit: int = 5) -> List[Dict[str, Any]]:
        results = self.collection.query(
            query_embeddings=[embedding],
            n_results=limit,
        )
        
        if not results or "documents" not in results or not results["documents"][0]:
            return []
            
        ids = results["ids"][0]
        docs = results["documents"][0]
           
        return [
            {"id": i, "text": d}
            for i, d in zip(ids, docs)
        ]


class PgVectorStore(BaseVectorStore):
    def __init__(self):
        pass
        
    async def _init_table(self, conn):   
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
        await conn.execute(text('''
            CREATE TABLE IF NOT EXISTS v1_report_embeddings (
                report_id VARCHAR PRIMARY KEY,
                content TEXT NOT NULL,
                embedding vector(768)
            );
        '''))
        
    async def upsert(self, doc_id: str, text_content: str, embedding: List[float]):        
        async with async_session() as session:
            async with session.begin():
                await self._init_table(session)
                stmt = text('''
                    INSERT INTO v1_report_embeddings (report_id, content, embedding)
                    VALUES (:id, :content, :emb)
                    ON CONFLICT (report_id) DO UPDATE SET
                    content = EXCLUDED.content,
                    embedding = EXCLUDED.embedding
                ''')
                await session.execute(stmt, {
                    "id": doc_id,
                    "content": text_content,
                    "emb": str(embedding)
                })
                
    async def search(self, embedding: List[float], limit: int = 5) -> List[Dict[str, Any]]:      
        async with async_session() as session:
            await self._init_table(session)
            query = "SELECT report_id, content FROM v1_report_embeddings"
            params = {"emb": str(embedding), "limit": limit}
            query += " ORDER BY embedding <-> :emb LIMIT :limit"
            result = await session.execute(text(query), params)
            rows = result.fetchall()
            
            return [
            {
                "id": row.report_id, 
                "text": row.content, 
            } 
            for row in rows
            ]


_vector_store_instance = None

def get_vector_store() -> BaseVectorStore:
    global _vector_store_instance

    if _vector_store_instance is None:
        if settings.ENVIRONMENT == "development":
            _vector_store_instance = ChromaVectorStore()       
        else:
            _vector_store_instance = PgVectorStore()
        
    return _vector_store_instance