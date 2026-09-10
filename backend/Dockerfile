FROM python:3.12-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY app/ app/
COPY seed.py .
COPY run.py .

# Create ml_models directory
RUN mkdir -p ml_models

# Expose port
EXPOSE 8000

# Run
CMD ["python", "run.py"]
