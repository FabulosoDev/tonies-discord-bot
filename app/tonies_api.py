import os
import httpx
from google.protobuf.message import DecodeError
from tafHeader_pb2 import TonieboxAudioFileHeader
from logger_factory import DefaultLoggerFactory

logger = DefaultLoggerFactory.get_logger(__name__)

class ToniesApi:
    def __init__(self):
        self.cert_path = os.getenv("CLIENT_CERT_PATH")
        self.key_path = os.getenv("CLIENT_KEY_PATH")
        if not self.cert_path or not self.key_path:
            logger.error("Missing required environment variables: CLIENT_CERT_PATH and/or CLIENT_KEY_PATH")
        logger.debug(f"ToniesApi initialized with cert_path: {self.cert_path}, key_path: {self.key_path}")

    async def get_audio_id(self, ruid: str, auth: str):
        if not ruid:
            logger.error("Missing required parameter: ruid")
            raise ValueError("Missing required parameter: ruid")
        if not auth:
            logger.error("Missing required parameter: auth")
            raise ValueError("Missing required parameter: auth")

        logger.info(f"Fetching audio_id for ruid: {ruid}")
        headers = {
            "Authorization": f"BD {auth}",
            "Range": "bytes=0-4095"  # Request only the first 4096 bytes
        }

        async with httpx.AsyncClient(verify=False, cert=(self.cert_path, self.key_path)) as client:
            try:
                logger.debug(f"Making request to https://prod.de.tbs.toys:443/v2/content/{ruid}")
                response = await client.get(
                    f"https://prod.de.tbs.toys:443/v2/content/{ruid}",
                    headers=headers
                )
            except Exception as e:
                logger.error(f"External request failed: {str(e)}")
                return {"error": f"External request failed: {str(e)}"}

            if response.status_code not in (200, 206):
                logger.error(f"Unexpected response code: {response.status_code}")
                return {"error": f"Unexpected response code: {response.status_code}"}

            try:
                content = response.content
                logger.debug("Parsing header length from response content")
                # Read first 4 bytes for header length (big-endian)
                header_length = int.from_bytes(content[:4], byteorder='big')
                logger.debug(f"Header length: {header_length} bytes")

                # Extract header data based on header_length
                header_data = content[4:4+header_length]
                if len(header_data) != header_length:
                    logger.error(f"Header data length mismatch. Expected: {header_length}, Got: {len(header_data)}")
                    return {"error": "Failed to read complete header data"}

                # Parse the header data into a TonieboxAudioFileHeader message
                logger.debug("Parsing protobuf header data")
                taf_header = TonieboxAudioFileHeader()
                taf_header.ParseFromString(header_data)

                # Return the audio_id as string
                audio_id = str(taf_header.audio_id)
                logger.info(f"Successfully extracted audio_id: {audio_id}")
                return {"audio_id": audio_id}
            except DecodeError as e:
                logger.error(f"Failed to parse protobuf data: {str(e)}")
                return {"error": "Failed to parse protobuf data"}
            except Exception as e:
                logger.error(f"Error processing header: {str(e)}")
                return {"error": f"Error processing header: {str(e)}"}

        logger.warning("No audio_id found in response")
        return {"error": "No audio_id found"}