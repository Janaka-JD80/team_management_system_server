from google import genai
from groq import Groq
import asyncio
from typing import List, Dict, Any
from fastapi import HTTPException
from app.core.config import settings

class LlmClient:
    def __init__(self):
        if settings.GEMINI_API_KEY:
            self.genai_client = genai.Client(api_key=settings.GEMINI_API_KEY)
        else:
            self.genai_client = None
        
        if settings.GROQ_API_KEY:
            self.groq_client = Groq(api_key=settings.GROQ_API_KEY)
        else:
            self.groq_client = None

    async def get_embedding(self, text: str) -> List[float]:
        if not self.genai_client:
            raise HTTPException(status_code=500, detail="LLM Client is not configured")
            
        try:
            result = await asyncio.to_thread(
                self.genai_client.models.embed_content,
                model="gemini-embedding-2",
                contents=text
            )
            return result.embeddings[0].values
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to generate embedding: {str(e)}")

    async def generate_chat(self, system_prompt: str, user_message: str) -> str:

        if not self.groq_client:
            raise HTTPException(status_code=500, detail="LLM Client is not configured")
            
        try:
            chat_completion = await asyncio.to_thread(
                self.groq_client.chat.completions.create,
                messages=[
                    {
                        "role": "system",
                        "content": system_prompt,
                    },
                    {
                        "role": "user",
                        "content": user_message,
                    }
                ],
                model="openai/gpt-oss-20b",
                temperature=0.0,
                max_tokens=1024
            )
            return chat_completion.choices[0].message.content
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to generate chat: {str(e)}")

llm_client = LlmClient()
