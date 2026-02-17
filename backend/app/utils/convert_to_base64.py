import base64


def convert_to_base64(file_data):
    """
    Converts a JPEG file data to base64 encoded string.

    Args:
        file_data (bytes): The binary data of the JPEG file.

    Returns:
        str: The base64 encoded string representation of the file data.
    """
    base64_data = base64.b64encode(file_data)
    base64_string = base64_data.decode("utf-8")
    return base64_string
