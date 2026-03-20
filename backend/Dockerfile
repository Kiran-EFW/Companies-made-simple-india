FROM python:3.12-slim

# Install system dependencies required by WeasyPrint and other native libs
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    pkg-config \
    libcairo2-dev \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libgdk-pixbuf-2.0-0 \
    libffi-dev \
    shared-mime-info \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

# Cloud Run injects PORT env var (default 8080)
ENV PORT=8080
EXPOSE ${PORT}
CMD exec uvicorn src.main:app --host 0.0.0.0 --port ${PORT}
