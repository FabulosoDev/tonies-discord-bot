import os
import httpx
import asyncio
from datetime import datetime

class ToniesJson:
    def __init__(self):
        self.json_url = os.getenv("JSON_URL")
        self.json_data = None
        self._update_task = None

    async def fetch_json(self):
        while True:
            async with httpx.AsyncClient() as client:
                try:
                    response = await client.get(self.json_url)
                    response.raise_for_status()
                    self.json_data = response.json()
                    print(f"JSON data updated at {datetime.now()}")
                except httpx.HTTPError as e:
                    print(f"Failed to fetch JSON: {e}")
            await asyncio.sleep(24 * 60 * 60)  # 24 hours in seconds

    def start_updates(self):
        self._update_task = asyncio.create_task(self.fetch_json())

    def find_by_audio_id(self, audio_id: str) -> dict | None:
        """Find a tonie by its audio_id in the cached JSON data"""
        if not self.json_data:
            return None
        
        return next(
            (item for item in self.json_data 
             if str(audio_id) in item.get("audio_id", [])), 
            None
        )