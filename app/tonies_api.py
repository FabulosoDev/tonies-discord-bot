import os
import httpx
from google.protobuf.message import DecodeError
from tafHeader_pb2 import TonieboxAudioFileHeader

class ToniesApi:
    def __init__(self):
        self.cert_path = os.getenv("CLIENT_CERT_PATH")
        self.key_path = os.getenv("CLIENT_KEY_PATH")

    async def get_audio_id(self, ruid: str, auth: str):
        if not ruid:
            raise ValueError("Missing required parameter: ruid")
        if not auth:
            raise ValueError("Missing required parameter: auth")

        headers = {
            "Authorization": f"BD {auth}",
            "Range": "bytes=0-4095"  # Request only the first 4096 bytes
        }

        async with httpx.AsyncClient(verify=False, cert=(self.cert_path, self.key_path)) as client:
            try:
                response = await client.get(
                    f"https://prod.de.tbs.toys:443/v2/content/{ruid}",
                    headers=headers
                )
            except Exception as e:
                return {"error": f"External request failed: {str(e)}"}

            if response.status_code not in (200, 206):
                return {"error": f"Unexpected response code: {response.status_code}"}

            try:
                content = response.content
                # Read first 4 bytes for header length (big-endian)
                header_length = int.from_bytes(content[:4], byteorder='big')

                # Extract header data based on header_length
                header_data = content[4:4+header_length]
                if len(header_data) != header_length:
                    return {"error": "Failed to read complete header data"}

                # Parse the header data into a TonieboxAudioFileHeader message
                taf_header = TonieboxAudioFileHeader()
                taf_header.ParseFromString(header_data)
                
                # Return the audio_id as string
                return {"audio_id": str(taf_header.audio_id)}
            except DecodeError:
                return {"error": "Failed to parse protobuf data"}
            except Exception as e:
                return {"error": f"Error processing header: {str(e)}"}

        return {"error": "No audio_id found"}