# backend/app/services/api_service_external/api_proprietary_access/api_openai/speech_synthesis_service.py
import os
import re
from io import BytesIO

from dotenv import load_dotenv
from openai import OpenAI
from pydub import AudioSegment
from pydub.effects import speedup

from backend.app.services.google_services.upload_files_to_gcs_service.gcs_upload_service import \
    GCSUploadService
from backend.app.services.logging_service.logger import LoggingUtility

# Create an instance of the LoggingUtility class
logging_utility = LoggingUtility()


class SpeechSynthesisService:
    def __init__(self, api_key, voice="echo", pitch=-0.2, speed=1.14):
        self.client = OpenAI(api_key=api_key)
        self.voice = voice
        self.pitch = pitch
        self.speed = speed

    def chunk_text(self, text, length=4096):
        # Split text into chunks of 'length' characters each
        text = re.sub(
            r"\s+", " ", text
        )  # Replace multiple whitespace with a single space
        chunks = [text[i : i + length] for i in range(0, len(text), length)]
        return chunks

    def generate_speech_for_chunk(self, text_chunk):
        # Generate speech using OpenAI's API for a single chunk of text
        response = self.client.audio.speech.create(
            model="tts-1-hd", voice=self.voice, input=text_chunk
        )
        audio_bytes = response.read()
        audio = AudioSegment.from_file(BytesIO(audio_bytes), format="mp3")
        return audio

    def adjust_audio_properties(self, audio):
        # Apply pitch shift
        new_sample_rate = int(audio.frame_rate * (2.0**self.pitch))
        lowpitch_audio = audio._spawn(
            audio.raw_data, overrides={"frame_rate": new_sample_rate}
        )
        lowpitch_audio = lowpitch_audio.set_frame_rate(audio.frame_rate)

        # Apply speed modification
        speed_corrected_audio = speedup(lowpitch_audio, playback_speed=self.speed)
        return speed_corrected_audio

    def generate_speech(self, text, user_id, thread_id, message_id):
        logging_utility.info("Generating speech for text: %s", text)

        try:
            # Step 1: Chunk the text
            chunks = self.chunk_text(text)

            # Step 2: Process each chunk
            audio_parts = []
            for chunk in chunks:
                audio_part = self.generate_speech_for_chunk(chunk)
                adjusted_audio = self.adjust_audio_properties(audio_part)
                audio_parts.append(adjusted_audio)

            # Step 3: Combine the results
            combined_audio = sum(audio_parts[1:], audio_parts[0])

            # Save the adjusted audio to a file-like object
            adjusted_audio_buffer = BytesIO()
            combined_audio.export(adjusted_audio_buffer, format="mp3")
            adjusted_audio_buffer.seek(0)

            # Step 4: Upload the speech file to GCS
            gcs_upload_service = GCSUploadService(bucket_name="q_speech_retrieval")
            public_url = gcs_upload_service.upload_speech_file(
                adjusted_audio_buffer, user_id, thread_id, message_id
            )
            logging_utility.info(
                "Speech file uploaded to GCS with public URL: %s", public_url
            )

            return public_url

        except Exception as e:
            logging_utility.error(
                "An error occurred while generating speech: %s", str(e)
            )
            return None


if __name__ == "__main__":
    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")
    service = SpeechSynthesisService(api_key, voice="echo", pitch=-0.2, speed=1.14)
    user_id = "user123"
    thread_id = "thread456"
    message_id = "msg789"
    service.generate_speech(
        "You will give the people of Earth an ideal to strive towards. They will race behind you, they will stumble, they will fall. But in time, they will join you in the sun, Kal. In time, you will help them accomplish wonders.",
        user_id,
        thread_id,
        message_id,
    )
