user_location_functions = [
    {
        "type": "function",
        "function": {
            "name": "getUserLocations",
            "description": "Retrieves user locations based on the user faux identity in your instructions",
            "parameters": {
                "type": "object",
                "properties": {
                    "faux_identity": {
                        "type": "string",
                        "description": "The faux identity of the user",
                    },
                    "limit": {
                        "type": "integer",
                        "description": "The maximum number of user locations to retrieve (optional)",
                    },
                },
                "required": ["faux_identity"],
            },
        },
    }
]
