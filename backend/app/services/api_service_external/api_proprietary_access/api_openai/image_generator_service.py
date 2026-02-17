import os

from dotenv import load_dotenv
from openai import OpenAI

from backend.app.services.logging_service.logger import LoggingUtility

load_dotenv()


class ImageGeneratorService:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_DALLE3_API_KEY"))
        self.logging_utility = LoggingUtility()

    def generate_image(self, prompt, size="1024x1024", quality="standard", n=1):
        """
        Generate an image based on the specified parameters.
        :param prompt: Description of the image to generate.
        :param size: Size of the image.
        :param quality: Quality of the image (standard or enhanced).
        :param n: Number of images to generate.
        :return: URL of the generated image.
        """
        try:
            self.logging_utility.info(
                "Entering generate_image with prompt='%s', size='%s', quality='%s', n=%d",
                prompt,
                size,
                quality,
                n,
            )

            response = self.client.images.generate(
                model="dall-e-3", prompt=prompt, size=size, quality=quality, n=n
            )

            image_url = response.data[0].url
            self.logging_utility.info(
                "Image generated successfully. URL: %s", image_url
            )

            return image_url
        except Exception as e:
            self.logging_utility.error(
                "An error occurred during image generation: %s", str(e)
            )
            return None


# Example usage
if __name__ == "__main__":
    image_gen_service = ImageGeneratorService()
    result = image_gen_service.generate_image("a white siamese cat")
    if result:
        image_gen_service.logging_utility.info("Image URL: %s", result)
    else:
        image_gen_service.logging_utility.warning("Failed to generate image.")
