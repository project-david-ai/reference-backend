import os
from dotenv import load_dotenv


load_dotenv()

secret_key = os.getenv('SECRET_KEY')

print(secret_key)  # Output: your_secret_key_here