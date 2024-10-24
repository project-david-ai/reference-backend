import os
import time
import uuid
from io import BytesIO
from dotenv import load_dotenv
import requests
from elevenlabs import VoiceSettings
from elevenlabs.client import ElevenLabs

from backend.app.services.google_services.upload_files_to_gcs_service.gcs_upload_service import GCSUploadService
from backend.app.services.logging_service.logger import LoggingUtility

# Create an instance of the LoggingUtility class
logging_utility = LoggingUtility()


class ElevenSpeechSynthesisService:
    def __init__(self):
        self.api_key = os.getenv("ELEVENLABS_API_KEY")
        if not self.api_key:
            raise ValueError("ELEVENLABS_API_KEY environment variable not set")
        self.client = ElevenLabs(api_key=self.api_key)

    def text_to_speech_file(self, text: str, user_id: str, thread_id: str, message_id: str, voice_id: str) -> str:
        """
        Converts text to speech and saves the output as an MP3 file to a Google Cloud Storage bucket.
        This function uses the ElevenLabs client for text-to-speech conversion.
        It configures various parameters for the voice output and saves the resulting audio stream to an MP3 file with a unique name.
        The MP3 file is then uploaded to a Google Cloud Storage bucket, and the public URL is returned.

        Args:
            text (str): The text content to convert to speech.
            user_id (str): The ID of the user.
            thread_id (str): The ID of the thread.
            message_id (str): The ID of the message.
            voice_id (str): The ID of the selected voice.

        Returns:
            str: The public URL of the uploaded audio file in Google Cloud Storage.
        """
        logging_utility.info("Generating speech for text: %s", text)

        try:
            # Generate speech using ElevenLabs API
            response = self.client.text_to_speech.convert(
                voice_id=voice_id,  # Use the provided voice ID
                optimize_streaming_latency="0",
                output_format="mp3_22050_32",
                text=text,
                model_id="eleven_turbo_v2",
                # use the turbo model for low latency, for other languages use the `eleven_multilingual_v2`
                voice_settings=VoiceSettings(
                    stability=0.0,
                    similarity_boost=1.0,
                    style=0.0,
                    use_speaker_boost=True,
                ),
            )
            logging_utility.info("Speech generated successfully")

            # Save the response as an audio file in memory
            audio_buffer = BytesIO()
            for chunk in response:
                if chunk:
                    audio_buffer.write(chunk)
            audio_buffer.seek(0)  # Reset the buffer position to the beginning

            # Upload the speech file to GCS
            gcs_upload_service = GCSUploadService(bucket_name="q_speech_retrieval")
            public_url = gcs_upload_service.upload_speech_file(audio_buffer, user_id, thread_id, message_id)
            logging_utility.info("Speech file uploaded to GCS with public URL: %s", public_url)

            return public_url

        except Exception as e:
            logging_utility.error("An error occurred while generating speech: %s", str(e))
            raise

    def get_available_voices(self):
        """
        Retrieves the list of available voices from the ElevenLabs API.

        Returns:
            list: A list of dictionaries, each representing a voice.
        """
        url = "https://api.elevenlabs.io/v1/voices"
        headers = {
            "Accept": "application/json",
            "xi-api-key": self.api_key,
            "Content-Type": "application/json"
        }

        response = requests.get(url, headers=headers)
        data = response.json()

        return data['voices']


if __name__ == "__main__":
    load_dotenv()
    service = ElevenSpeechSynthesisService()
    text = "Hello, world! This is a test of the ElevenLabs API."
    user_id = "user123"
    thread_id = "thread456"
    message_id = "msg789"
    #service.text_to_speech_file(text, user_id, thread_id, message_id)
    print (service.get_available_voices())
