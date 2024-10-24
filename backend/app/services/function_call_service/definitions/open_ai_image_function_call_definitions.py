# open_ai_image_function_call_definitions.py

image_functions = [
    {
        "type": "function",
        "function": {
            "name": "generateImage",
            "description": "Generate an image based on the user's request",
            "parameters": {
                "type": "object",
                "properties": {
                    "imageDescription": {
                        "type": "string",
                        "description": "The description of the image to be generated"
                    },
                    "size": {
                        "type": "string",
                        "description": "The size of the image (e.g., 1024x1024)",
                        "default": "1024x1024"
                    },
                    "quality": {
                        "type": "string",
                        "description": "The quality of the image (standard or enhanced)",
                        "enum": [
                            "standard",
                            "enhanced"
                        ],
                        "default": "standard"
                    },
                    "n": {
                        "type": "integer",
                        "description": "The number of images to generate",
                        "default": 1
                    }
                },
                "required": [
                    "imageDescription"
                ]
            }
        }
    }
]