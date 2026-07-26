FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY api/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY api /app/api

EXPOSE 8000

# Run uvicorn as non-root user
USER 1000

CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
