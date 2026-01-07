import requests
from config import settings
import logging

logger = logging.getLogger("RealEgo")

class Mem0Service:
    def __init__(self):
        self.api_url = settings.MEM0_API_URL
        self.api_key = settings.MEM0_API_KEY
        self.headers = {
            "Authorization": f"Token {self.api_key}",
            "Content-Type": "application/json"
        }

    def add_memory(self, content: str, user_id: str):
        # Using mem0 API to add memory
        # Assuming API structure based on typical memory service or generic usage
        # Endpoint might be /v1/memories/
        url = f"{self.api_url}/v1/memories/"
        data = {
            "messages": [{"role": "user", "content": content}],
            "user_id": str(user_id)
        }
        try:
            logger.debug(f"Adding memory to Mem0: {url}, data: {data}")
            response = requests.post(url, json=data, headers=self.headers)
            response.raise_for_status()
            logger.debug(f"Memory added successfully: {response.json()}")
            return response.json()
        except Exception as e:
            logger.error(f"Error adding memory: {e}")
            return None

    def search_memory(self, query: str, user_id: str):
        # Endpoint might be /v1/memories/search/
        url = f"{self.api_url}/v1/memories/search/"
        data = {
            "query": query,
            "user_id": str(user_id)
        }
        try:
            logger.debug(f"Searching memory in Mem0: {url}, data: {data}")
            response = requests.post(url, json=data, headers=self.headers)
            response.raise_for_status()
            result = response.json()
            logger.debug(f"Memory search result: {result}")
            return result
        except Exception as e:
            logger.error(f"Error searching memory: {e}")
            return []

mem0_service = Mem0Service()
