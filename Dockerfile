# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set environment variables to prevent interactive prompts during installation
ENV DEBIAN_FRONTEND=noninteractive

# Install the necessary LaTeX packages (THIS IS THE CRUCIAL STEP)
RUN apt-get update && \
    apt-get install -y texlive-latex-base texlive-fonts-recommended --no-install-recommends && \
    rm -rf /var/lib/apt/lists/*

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your application code into the container
COPY . .

# Command to run your FastAPI application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]