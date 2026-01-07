import requests
from config import settings

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
            response = requests.post(url, json=data, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error adding memory: {e}")
            return None

    def search_memory(self, query: str, user_id: str):
        # Endpoint might be /v1/memories/search/
        url = f"{self.api_url}/v1/memories/search/"
        data = {
            "query": query,
            "user_id": str(user_id)
        }
        try:
            response = requests.post(url, json=data, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error searching memory: {e}")
            return []

mem0_service = Mem0Service()
