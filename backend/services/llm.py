from openai import OpenAI
from config import settings
from .mem0 import mem0_service
import logging

logger = logging.getLogger("RealEgo")

class LLMService:
    def __init__(self):
        try:
            self.client = OpenAI(
                api_key=settings.ARK_API_KEY or "dummy", # Prevent crash if env var missing
                base_url=settings.ARK_API_URL
            )
        except Exception as e:
            logger.error(f"Failed to init LLM client: {e}")
            self.client = None
        self.model = settings.ARK_MODEL

    def chat(self, message: str, user_id: str, user_profile: dict):
        if not self.client:
            logger.error("LLM Service not available (Configuration missing).")
            return "LLM Service not available (Configuration missing)."
        
        logger.debug(f"Starting LLM chat for user {user_id}")

        # 1. Search relevant memories
        memories = mem0_service.search_memory(message, user_id)
        
        # 2. Construct system prompt with profile and memories
        system_prompt = f"You are a helpful assistant for {user_profile.get('username', 'User')}."
        
        profile_text = "User Profile:\n"
        if user_profile.get('full_name'): profile_text += f"Name: {user_profile['full_name']}\n"
        if user_profile.get('birth_date'): profile_text += f"Birth Date: {user_profile['birth_date']}\n"
        if user_profile.get('location'): profile_text += f"Location: {user_profile['location']}\n"
        # ... add more fields
        
        memory_text = "Relevant Memories:\n"
        if memories:
            for mem in memories:
                # Assuming mem structure, adjust as needed
                # mem0 usually returns list of dicts with 'memory' key
                mem_content = mem.get('memory', mem) if isinstance(mem, dict) else mem
                memory_text += f"- {mem_content}\n"
        
        system_prompt += f"\n\n{profile_text}\n\n{memory_text}"
        
        logger.debug(f"Constructed System Prompt: {system_prompt}")
        logger.debug(f"User Message: {message}")
        
        # 3. Call LLM
        try:
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": message}
                ]
            )
            response = completion.choices[0].message.content
            
            logger.debug(f"LLM Raw Response: {response}")
            
            # 4. Save interaction to memory (optional, but good for context)
            # mem0_service.add_memory(f"User asked: {message}\nAssistant answered: {response}", user_id)
            
            return response
        except Exception as e:
            logger.error(f"LLM Error: {e}")
            return "Sorry, I encountered an error processing your request."

llm_service = LLMService()
