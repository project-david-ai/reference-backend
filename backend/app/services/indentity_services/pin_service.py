import random
import string
from datetime import datetime


class PinService:

    @staticmethod
    def generate_pin(length=6):
        """
        Generate a random PIN of the specified length.

        Args:
            length (int, optional): Length of the generated PIN. Defaults to 6.

        Returns:
            str: A randomly generated PIN.
        """
        return "".join(random.choices(string.digits, k=length))

    @staticmethod
    def is_pin_expired(expiry_time):
        """
        Check if the provided expiry time is in the past.

        Args:
            expiry_time (datetime): The expiration time of the PIN.

        Returns:
            bool: True if the PIN is expired, otherwise False.
        """
        return datetime.utcnow() > expiry_time

    def is_pin_valid(self, provided_pin):
        """
        Checks if the provided PIN matches the stored PIN and if it's not expired.

        Args:
            provided_pin (str): The PIN provided by the user.

        Returns:
            bool: True if the PIN is valid, else False.
        """
        return self.user.password_reset_pin == provided_pin and not self.is_pin_expired(
            self.user.password_reset_expires_at
        )
