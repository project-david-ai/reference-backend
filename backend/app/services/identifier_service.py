import random
import string


class IdentifierService:
    @staticmethod
    def generate_id(prefix: str, length: int = 22) -> str:
        """Generate a prefixed ID with a specified length of random alphanumeric characters."""
        characters = string.ascii_letters + string.digits
        random_string = "".join(random.choice(characters) for _ in range(length))
        return f"{prefix}_{random_string}"

    @staticmethod
    def generate_custom_id(prefix: str) -> str:
        """Generate a custom ID with a given prefix."""
        return IdentifierService.generate_id(prefix)

    @staticmethod
    def generate_user_id() -> str:
        """Generate an assistant ID in the specified format."""
        return IdentifierService.generate_id("usr")

    @staticmethod
    def generate_profile_id() -> str:
        """Generate an assistant ID in the specified format."""
        return IdentifierService.generate_id("prf")


# Example usage:
if __name__ == "__main__":
    print(IdentifierService.generate_user_id())
    print(IdentifierService.generate_custom_id("custom"))
