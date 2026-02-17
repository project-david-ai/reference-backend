from backend.app.services.logging_service.logger import LoggingUtility

logging_utility = LoggingUtility()


class LocationHandler:
    def __init__(self):
        self.logging_utility = LoggingUtility()

    def handle_get_location_info(self, arguments):
        location = arguments["location"]
        location_info = self.fetch_location_info(location)
        return location_info

    def fetch_location_info(self, location):
        self.logging_utility.info("Fetching location information for: %s", location)
        # For demonstration purposes, let's simulate a successful API call
        return f"Location: {location}, Country: USA, Population: 2,000,000"
