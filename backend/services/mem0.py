from mem0 import MemoryClient
from config import settings
import logging
import asyncio
from functools import partial

logger = logging.getLogger("RealEgo")

class Mem0Service:
    def __init__(self):
        self.client = MemoryClient(
            host=settings.MEM0_API_URL,
            api_key=settings.MEM0_API_KEY
        )

    async def add_memory(self, messages: list, user_id: str):
        """
        Add memory asynchronously (non-blocking for the event loop).
        messages: List of dicts, e.g. [{"role": "user", "content": "..."}, ...]
        """
        loop = asyncio.get_running_loop()
        try:
            # async_mode=True tells the Mem0 server to process this as a background job
            func = partial(self.client.add, messages, user_id=user_id, async_mode=True)
            result = await loop.run_in_executor(None, func)
            logger.info(f"Memory add job submitted: {result}")
            return result
        except Exception as e:
            logger.error(f"Error adding memory: {e}")
            return None

    async def search_memory(self, query: str, user_id: str):
        """
        Search memory asynchronously (non-blocking for the event loop).
        Returns a list of memory items.
        """
        loop = asyncio.get_running_loop()
        try:
            func = partial(self.client.search, query, user_id=user_id)
            result = await loop.run_in_executor(None, func)
            # Ensure we return a list. result is typically {'results': [...]}
            if isinstance(result, dict):
                return result.get("results", [])
            return result if isinstance(result, list) else []
        except Exception as e:
            logger.error(f"Error searching memory: {e}")
            return []

mem0_service = Mem0Service()
