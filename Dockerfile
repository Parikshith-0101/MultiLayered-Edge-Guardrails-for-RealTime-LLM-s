# Use a lightweight Python image
FROM python:3.11-slim

# Set the working directory
WORKDIR /app

# Copy the requirements and install them
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the environment file and the codebase
COPY .env .
COPY backend_api/ ./backend_api/
COPY guardrails/ ./guardrails/

# Expose the FastAPI port
EXPOSE 8000

# Boot the server (Using host.docker.internal to reach local Ollama)
CMD ["uvicorn", "backend_api.main:app", "--host", "0.0.0.0", "--port", "8000"]