# syntax=docker/dockerfile:1
FROM --platform=$BUILDPLATFORM python:3.11-slim

# Create app directory
WORKDIR /app

# Install runtime dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source
COPY . .

# Expose the port your FastAPI app uses
EXPOSE 6996

# Default command
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "6996"]
