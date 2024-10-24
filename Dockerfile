# Use the official Python image from the Docker Hub
FROM python:3.8-slim

# Install necessary dependencies including git, curl, gcc, and build tools
RUN apt-get update && apt-get install -y \
    git \
    curl \
    gcc \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory inside the container
WORKDIR /code

# Copy the requirements file into the working directory
COPY requirements.txt /code/

# Install dependencies
RUN pip install --no-cache-dir --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the working directory
COPY . /code/

# Expose the port the app runs on
EXPOSE 5000

# Run the application
CMD ["python", "run.py"]
