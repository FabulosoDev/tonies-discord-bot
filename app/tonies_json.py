import os
import httpx
import asyncio
from datetime import datetime
from logger_factory import DefaultLoggerFactory

logger = DefaultLoggerFactory.get_logger(__name__)

class ToniesJson:
    def __init__(self):
        self.json_url = os.getenv("JSON_URL")
        if not self.json_url:
            logger.error("JSON_URL environment variable not set")
        self.json_data = None
        self._update_task = None
        logger.debug(f"ToniesJson initialized with URL: {self.json_url}")

    async def fetch_json(self):
        while True:
            logger.debug("Starting JSON fetch cycle")
            async with httpx.AsyncClient() as client:
                try:
                    logger.debug(f"Fetching JSON from {self.json_url}")
                    response = await client.get(self.json_url)
                    response.raise_for_status()
                    self.json_data = response.json()
                    logger.info(f"JSON data updated successfully at {datetime.now()}, entries: {len(self.json_data)}")
                except httpx.HTTPError as e:
                    logger.error(f"Failed to fetch JSON: {e}")
                except Exception as e:
                    logger.error(f"Unexpected error while fetching JSON: {str(e)}")
            logger.debug("Sleeping for 24 hours before next update")
            await asyncio.sleep(24 * 60 * 60)  # 24 hours in seconds

    def start_updates(self):
        logger.info("Starting periodic JSON updates")
        self._update_task = asyncio.create_task(self.fetch_json())

    def find_by_audio_id(self, audio_id: str) -> dict | None:
        """Find a tonie by its audio_id in the cached JSON data"""
        if not self.json_data:
            logger.warning("No JSON data available for search")
            return None
        
        logger.info(f"Searching for audio_id: {audio_id}")
        result = next(
            (item for item in self.json_data 
             if str(audio_id) in item.get("audio_id", [])), 
            None
        )
        
        if result:
            logger.info(f"Found tonie for audio_id {audio_id}: {result.get('series', 'Unknown')} - {result.get('episodes', 'Unknown')}")
        else:
            logger.warning(f"No tonie found for audio_id: {audio_id}")
        
        return result