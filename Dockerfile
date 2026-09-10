# Multi-stage production Dockerfile for Pocket Option AI Analyzer Bot
FROM python:3.12-slim AS builder

WORKDIR /app

# Install system build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install python wheels
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Final runtime container
FROM python:3.12-slim AS runner

WORKDIR /app

# Copy installed python libraries from builder
COPY --from=builder /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH

# Copy application code
COPY . .

# Ensure data directory exists for SQLite
RUN mkdir -p /app/data

# Port 3000 default
EXPOSE 3000

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=3000

# Healthcheck
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:3000/health || exit 1

CMD ["python", "main.py", "--mode", "server"]
