from openai import AsyncOpenAI
from config import settings
from .mem0 import mem0_service
import logging

logger = logging.getLogger("RealEgo")

class LLMService:
    def __init__(self):
        try:
            self.client = AsyncOpenAI(
                api_key=settings.ARK_API_KEY or "dummy", # Prevent crash if env var missing
                base_url=settings.ARK_API_URL
            )
        except Exception as e:
            logger.error(f"Failed to init LLM client: {e}")
            self.client = None
        self.model = settings.ARK_MODEL

    async def chat(self, message: str, user_id: str, user_profile: dict, stream: bool = False):
        if not self.client:
            logger.error("LLM Service not available (Configuration missing).")
            return "LLM Service not available (Configuration missing)."
        
        logger.debug(f"Starting LLM chat for user {user_id}")

        # 1. Search relevant memories (Async)
        memories = await mem0_service.search_memory(message, user_id)
        
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
            logger.info(f"--- LLM REQUEST START ---")
            logger.info(f"Model: {self.model}")
            logger.info(f"System Prompt: {system_prompt}")
            logger.info(f"User Message: {message}")
            logger.info(f"--- LLM REQUEST END ---")

            if stream:
                completion = await self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": message}
                    ],
                    stream=True
                )
                return completion
            else:
                completion = await self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": message}
                    ]
                )
                response = completion.choices[0].message.content
                
                logger.info(f"--- LLM RESPONSE START ---")
                logger.info(f"Response Content: {response}")
                logger.info(f"--- LLM RESPONSE END ---")
                
                return response
        except Exception as e:
            logger.error(f"LLM Error: {e}", exc_info=True)
            return "Sorry, I encountered an error processing your request."

    async def process_voice_profile(self, audio_file, current_timeline: dict):
        """
        1. Transcribe audio
        2. Extract structured profile data
        3. Merge with current timeline
        """
        if not self.client:
            return None, "LLM Service not available"

        try:
            # 1. Transcribe
            # Note: Ensure the model supports transcription or use specific whisper endpoint
            
            transcription = await self.client.audio.transcriptions.create(
                model="whisper-1", # Often standard alias
                file=audio_file
            )
            text = transcription.text
            logger.info(f"Transcribed text: {text}")

            # 2. Extract Info
            extraction_prompt = f"""
            You are a data extraction assistant.
            Extract information from the user's spoken input into the following JSON structure.
            Only update fields that are mentioned. Keep existing data if not contradicted.
            
            Categories:
            0: Birth (Time, Location, etc.)
            1: 0-6 years old experiences
            2: Primary/Secondary Education & Events
            3: Higher Education & Events
            4: Family Relations
            5: Social Relations (Friends)
            6: Work History
            7: Locations (Residence, Work, Past)
            8: Assets
            
            Current Data: {current_timeline}
            
            User Input: "{text}"
            
            Return ONLY the updated JSON. Keys must be: 
            "0_birth", "1_early_childhood", "2_primary_edu", "3_higher_edu", "4_family", "5_social", "6_work", "7_locations", "8_assets".
            Each value should be a string or object with details.
            """
            
            completion = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a precise data extractor. Output JSON only."},
                    {"role": "user", "content": extraction_prompt}
                ],
                response_format={ "type": "json_object" } # If supported, else prompt engineering
            )
            json_response = completion.choices[0].message.content
            return text, json_response

        except Exception as e:
            logger.error(f"Voice processing error: {e}", exc_info=True)
            return None, str(e)

llm_service = LLMService()
