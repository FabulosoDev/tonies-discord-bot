from typing import Optional
import os
import time
import httpx
from logger_factory import DefaultLoggerFactory

logger = DefaultLoggerFactory.get_logger(__name__)

class TeddyCloudApi:
    def __init__(self):
        """Initialize TeddycloudApi"""
        self.base_url = os.getenv("TEDDYCLOUD_API")
        if not self.base_url:
            logger.error("TEDDYCLOUD_API environment variable not set")
            raise ValueError("TEDDYCLOUD_API environment variable not set")

    async def add_tonie(self, ruid: str, auth: str) -> dict:
        """Add a new tonie to Teddycloud"""
        url = f"{self.base_url}/v2/content/{ruid}"
        host = self.base_url.split('//')[1]
        headers = {
            'Authorization': f'BD {auth}',
            'Host': host
        }

        start_time = time.time()
        async with httpx.AsyncClient(timeout=60.0) as client:
            try:
                logger.debug(f"Adding tonie with RUID {ruid} to Teddycloud")
                response = await client.get(url, headers=headers)
                elapsed = time.time() - start_time
                logger.info(f"Request completed in {elapsed:.2f} seconds")
            except Exception as e:
                elapsed = time.time() - start_time
                logger.error(f"Request failed after {elapsed:.2f} seconds: {str(e)}")
                return {"success": False, "error": f"External request failed: {str(e)}"}

            if response.status_code not in (200, 206):
                logger.error(f"Unexpected response code: {response.status_code}")
                return {"success": False, "error": f"Unexpected response code: {response.status_code}"}

            return {"success": True}
