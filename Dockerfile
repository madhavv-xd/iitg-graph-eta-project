# Use an official Python lightweight image
FROM python:3.12-slim

# Set working directory inside the container
WORKDIR /app

# Copy the pyproject.toml first to install dependencies
COPY pyproject.toml .

# Install dependencies directly from pyproject.toml
RUN pip install --no-cache-dir .

# Copy the rest of the project (src, data, etc.)
COPY . /app

# The port Railway assigns automatically
EXPOSE 8000

# VERY IMPORTANT: Tell the code where to find the data folder
# Railway mounts everything inside /app
ENV DATA_DIR="/app/data/processed"

# Move to the src directory where main.py lives
WORKDIR /app/src

# Command to run the FastAPI app
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
