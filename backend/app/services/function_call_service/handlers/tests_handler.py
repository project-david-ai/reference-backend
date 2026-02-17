import random

from backend.app.services.logging_service.logger import LoggingUtility

logging_utility = LoggingUtility()


class TestsHandler:
    def __init__(self):
        self.logging_utility = LoggingUtility()

    @staticmethod
    def get_flight_times(departure: str, arrival: str) -> dict:
        """
        Simulate flight times between two cities (airport codes).

        Parameters:
            departure (str): The departure city (airport code).
            arrival (str): The arrival city (airport code).

        Returns:
            dict: A mock response with flight times and airports.
        """
        # Randomly generate flight time between 1 to 12 hours
        flight_time = random.randint(1, 12)
        flight_minutes = random.randint(0, 59)
        flight_duration = f"{flight_time} hours {flight_minutes} minutes"

        return {
            "departure": departure,
            "arrival": arrival,
            "flight_time": flight_duration,
        }

    # Example usage:
    response = get_flight_times("LAX", "JFK")
    print(response)
