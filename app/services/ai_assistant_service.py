from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any, List
import json
from fastapi import HTTPException
from app.integrations.llm_client import llm_client
from app.services.vector_store import get_vector_store
from app.repositories.report_repository import report_repository
from app.prompts.ai_prompts import get_rag_system_prompt

class AiAssistantService:

    async def sync_report_to_vector_db(self, db: AsyncSession, report_id: str):
      
        report = await report_repository.get_report_by_id(db, report_id)
        if not report or not report.versions:
            return    
        latest_version = report.versions[0]
        
        user_name = report.user.full_name if report.user else "Unknown Team Member"
        week_str = report.week_start_date.isoformat()
        
        content = f"Report for {user_name} (Week of {week_str}):\n"
        content += f"Status: {report.status.status_name}\n"
        
        if latest_version.tasks_completed:
            content += "Completed Tasks:\n" + "\n".join([f"- {t.get('task_name', 'Unnamed task')}" for t in latest_version.tasks_completed]) + "\n"
            
        if latest_version.blockers:
            content += "Blockers:\n" + "\n".join([f"- {b}" for b in latest_version.blockers]) + "\n"
            
        if latest_version.hours_worked_by_type:
            content += "Time Spent:\n" + "\n".join([f"- {k}: {v} hours" for k, v in latest_version.hours_worked_by_type.items()]) + "\n"
            
        embedding = await llm_client.get_embedding(content)
        vector_store = get_vector_store()
      
        await vector_store.upsert(
            doc_id=str(report.report_id),
            text=content,
            embedding=embedding,
        )

    async def generate_chat_response(self, db: AsyncSession, message: str) -> str:
    
        query_embedding = await llm_client.get_embedding(message)
        vector_store = get_vector_store()  
        relevant_chunks = await vector_store.search(
            embedding=query_embedding, 
            limit=5, 
        )
        
        context_str = "No relevant reports found."
        if relevant_chunks:
            context_str = "\n\n---\n\n".join([chunk["text"] for chunk in relevant_chunks])
            
        system_prompt = get_rag_system_prompt(context_str)
        response = await llm_client.generate_chat(
            system_prompt=system_prompt,
            user_message=message
        ) 
        return response

ai_assistant_service = AiAssistantService()
