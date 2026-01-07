import tos
from config import settings
import os

class TOSService:
    def __init__(self):
        self.endpoint = settings.TOS_ENDPOINT
        self.region = settings.TOS_REGION
        self.ak = settings.TOS_AK
        self.sk = settings.TOS_SK
        self.bucket = settings.TOS_BUCKET
        
        # Initialize client
        # Note: Assuming 'tos' package usage based on Volcengine standards
        try:
            self.client = tos.TosClientV2(
                self.ak,
                self.sk,
                self.endpoint,
                self.region
            )
            # Create bucket if not exists
            try:
                self.client.create_bucket(self.bucket)
            except Exception as e:
                # Bucket might already exist
                pass
        except Exception as e:
            print(f"Failed to initialize TOS client: {e}")
            self.client = None

    def upload_file(self, file_content, object_key):
        if not self.client:
            raise Exception("TOS Client not initialized")
        
        try:
            self.client.put_object(self.bucket, object_key, content=file_content)
            # Generate a signed URL or public URL if needed. 
            # For now returning the object key or direct link logic.
            return f"https://{self.bucket}.{self.endpoint}/{object_key}"
        except Exception as e:
            print(f"Upload failed: {e}")
            raise e

tos_service = TOSService()
