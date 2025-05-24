import os
import time
import uuid
from pathlib import Path
from typing import Optional
import requests
import json
import boto3

class VoiceService:
    def __init__(self, api_key: str, voice_id: str, cache_dir: Path):
        """Initialize voice service with ElevenLabs API key and voice ID."""
        self.api_key = api_key
        self.voice_id = voice_id
        self.cache_dir = cache_dir
        
        # Create cache directory if it doesn't exist
        if not self.cache_dir.exists():
            self.cache_dir.mkdir(parents=True)
    
    def text_to_speech(self, text: str) -> Optional[str]:
        """Convert text to speech and return the path to the audio file."""
        try:
            # Generate a unique filename
            filename = f"tts_{int(time.time())}.mp3"
            file_path = self.cache_dir / filename
            
            # Generate audio using ElevenLabs API directly
            url = f"https://api.elevenlabs.io/v1/text-to-speech/{self.voice_id}"
            
            headers = {
                "Accept": "audio/mpeg",
                "Content-Type": "application/json",
                "xi-api-key": self.api_key
            }
            
            data = {
                "text": text,
                "model_id": "eleven_multilingual_v2",
                "voice_settings": {
                    "stability": 0.5,
                    "similarity_boost": 0.5
                }
            }
            
            response = requests.post(url, json=data, headers=headers)
            
            if response.status_code != 200:
                print(f"Error from ElevenLabs API: {response.text}")
                return None
            
            # Save audio to file
            with open(file_path, "wb") as f:
                f.write(response.content)
            
            # Return path to audio file
            return str(file_path)
        except Exception as e:
            print(f"Error in text-to-speech conversion: {str(e)}")
            return None
    
    def text_to_speech_for_twilio(self, text: str) -> Optional[str]:
        """Convert text to speech and return URL for Twilio to play."""
        try:
            # Generate a unique filename
            filename = f"tts_{uuid.uuid4()}.mp3"
            
            # Generate audio using ElevenLabs API directly
            url = f"https://api.elevenlabs.io/v1/text-to-speech/{self.voice_id}"
            
            headers = {
                "Accept": "audio/mpeg",
                "Content-Type": "application/json",
                "xi-api-key": self.api_key
            }
            
            data = {
                "text": text,
                "model_id": "eleven_multilingual_v2",
                "voice_settings": {
                    "stability": 0.5,
                    "similarity_boost": 0.5
                }
            }
            
            response = requests.post(url, json=data, headers=headers)
            
            if response.status_code != 200:
                print(f"Error from ElevenLabs API: {response.text}")
                return None
                
            # Check if we should use S3 (for production) or local (for development)
            s3_bucket = os.getenv("S3_BUCKET_NAME")
            aws_access_key = os.getenv("AWS_ACCESS_KEY_ID")
            aws_secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")
            
            if s3_bucket and aws_access_key and aws_secret_key:
                # Upload to S3
                s3 = boto3.client(
                    's3', 
                    aws_access_key_id=aws_access_key,
                    aws_secret_access_key=aws_secret_key
                )
                
                s3.put_object(
                    Body=response.content,
                    Bucket=s3_bucket,
                    Key=filename,
                    ContentType='audio/mpeg',
                    ACL='public-read'
                )
                
                # Return the public URL
                return f"https://{s3_bucket}.s3.amazonaws.com/{filename}"
            else:
                # Local file fallback for development
                file_path = self.cache_dir / filename
                with open(file_path, "wb") as f:
                    f.write(response.content)
                
                # Return URL for local development
                base_url = os.getenv("BASE_URL", "http://localhost:5000")
                return f"{base_url}/static/audio_cache/{file_path.name}"
                
        except Exception as e:
            print(f"Error in text-to-speech conversion: {str(e)}")
            return None