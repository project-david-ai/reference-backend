user_functions = [
    {
        "type": "function",
        "function": {
            "name": "getUserDetailsByFauxIdentity",
            "description": "Retrieves user details based on the user faux identity in your instructions",
            "parameters": {
                "type": "object",
                "properties": {
                    "faux_identity": {
                        "type": "string",
                        "description": "The faux identity of the user",
                    }
                },
                "required": ["faux_identity"],
            },
        },
    }
]
