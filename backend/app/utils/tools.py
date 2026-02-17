def str_to_bool(s):
    """
    Converts a string representation of a boolean into its corresponding boolean value.

    Args:
    s (str): The string representation of a boolean, expected to be either 'True' or 'False'.

    Returns:
    bool: The boolean representation of the string.

    Raises:
    ValueError: If the input string is neither 'True' nor 'False'.
    """
    if s == "True":
        return True
    elif s == "False":
        return False
    else:
        raise ValueError("Invalid value for boolean conversion")
