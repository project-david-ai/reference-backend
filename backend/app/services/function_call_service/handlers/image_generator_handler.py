from backend.app.services.api_service_external.api_proprietary_access.api_openai.image_generator_service import ImageGeneratorService
from backend.app.services.logging_service.logger import LoggingUtility


class ImageGeneratorHandler:
    def __init__(self):

        self.logging_utility = LoggingUtility()
        self.image_gen_service = ImageGeneratorService()

    def handle_generate_image(self, arguments):
        image_description = arguments["imageDescription"]
        try:
            image_url = self.image_gen_service.generate_image(prompt=image_description)
            if image_url:
                return image_url
            else:
                return "Failed to generate image."
        except Exception as e:
            self.logging_utility.error("An error occurred while generating the image: %s", str(e))
            return "An error occurred while generating the image."

    def inform_image_capability_under_development(self, image_description):
        self.logging_utility.info('User requested image generation: %s', image_description)
        response = "I apologize for the inconvenience, but the image generation capability is currently under development. In the meantime, please speak with my brother David for any image-related requests. You can reach him at: https://chat.openai.com/g/g-7oUtFOMf3-david"
        return response
