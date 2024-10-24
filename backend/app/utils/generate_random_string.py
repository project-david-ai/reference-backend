import os
import string
import random


def generate_random_string(length=100):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for i in range(length))


random_endpoint = generate_random_string()
print(f"Random endpoint: {random_endpoint}")
