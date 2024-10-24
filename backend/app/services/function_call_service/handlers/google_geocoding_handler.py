from backend.app.services.api_service_external.api_proprietary_access.api_google.google_geocoding_service import GoogleGeocodingService
from backend.app.services.logging_service.logger import LoggingUtility


class GoogleGeocodingHandler:
    def __init__(self):
        self.google_geocoding_service = GoogleGeocodingService()
        self.logging_utility = LoggingUtility()

    def handle_get_current_location_by_gps(self, arguments):
        self.logging_utility.info('Retrieving current location by GPS')
        faux_identity = arguments.get("faux_identity", None)
        limit = arguments.get("limit", 1)

        if faux_identity:
            try:
                location = self.google_geocoding_service.get_current_location_by_gps(faux_identity, limit)
                response = "Current Location:\n"
                response += f"Formatted Address: {location['formatted_address']}\n"
                response += f"URL: {location['url']}\n"
                response += f"Latitude: {location['latitude']}\n"
                response += f"Longitude: {location['longitude']}\n"
            except Exception as e:
                self.logging_utility.error(f"Error retrieving current location by GPS: {str(e)}")
                response = "Error retrieving current location by GPS."
        else:
            self.logging_utility.warning('Faux identity not provided')
            response = "Faux identity not provided."

        return response

    def handle_get_places_near_by_gps(self, arguments):
        self.logging_utility.info('Retrieving places nearby by GPS')
        faux_identity = arguments.get("faux_identity", None)
        limit = arguments.get("limit", 1)
        place = arguments.get("place", None)

        if faux_identity and place:
            try:
                data = self.google_geocoding_service.get_places_near_by_gps(faux_identity, limit, place)
                response = "Nearby Places:\n"
                for i, place_data in enumerate(data['places'], start=1):
                    response += f"Place {i}:\n"
                    response += f"Name: {place_data['name']}\n"
                    response += f"Address: {place_data['vicinity']}\n"
                    response += f"Rating: {place_data['rating']}\n"
                    response += f"URL: {data['url']}\n\n"
            except Exception as e:
                self.logging_utility.error(f"Error retrieving places nearby by GPS: {str(e)}")
                response = "Error retrieving places nearby by GPS."
        else:
            self.logging_utility.warning('Faux identity or place not provided')
            response = "Faux identity or place not provided."

        return response