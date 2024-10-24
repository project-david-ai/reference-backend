google_map_functions = [
  {
    "type": "function",
    "function": {
      "name": "getCurrentLocationByGps",
      "description": "Retrieves the current location and traces back previous locations based on the last seen GPS coordinates for a given faux identity, use the user's faux_identity from instructions",
      "parameters": {
        "type": "object",
        "properties": {
          "faux_identity": {
            "type": "string",
            "description": "The faux identity associated with the user"
          },
          "limit": {
            "type": "integer",
            "description": "The maximum number of previous locations to retrieve"
          }
        },
        "required": ["faux_identity", "limit"]
      }
    }
  },
  {
    "type": "function",
    "function": {
      "name": "getPlacesNearByGps",
      "description": "Retrieves nearby places based on the last seen GPS coordinates for a given faux identity, use the user's faux_identity from instructions",
      "parameters": {
        "type": "object",
        "properties": {
          "faux_identity": {
            "type": "string",
            "description": "The faux identity associated with the user"
          },
          "limit": {
            "type": "integer",
            "description": "The maximum number of GPS locations to consider"
          },
          "place": {
            "type": "string",
            "description": "The type of place to search for (e.g., 'restaurant', 'cafe', 'store')"
          }
        },
        "required": ["faux_identity", "limit", "place"]
      }
    }
  }
]