# Stage 1: Build dependencies
FROM python:3.12-slim AS builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Create a virtual environment to isolate dependencies cleanly
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY requirements.txt .

# Install python dependencies in the virtual environment
RUN pip install --no-cache-dir -r requirements.txt

# Stage 2: Final runner image
FROM python:3.12-slim AS runner

WORKDIR /app

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Create a non-root group and user with a home directory
RUN groupadd -g 10001 appgroup && \
    useradd -r -u 10001 -g appgroup -m -d /home/appuser appuser
ENV HOME=/home/appuser


# Copy application code and set ownership to the non-root user
COPY --chown=appuser:appgroup ./app ./app

# Expose port
EXPOSE 8000

# Switch to the non-root user
USER appuser

# Use Gunicorn as the production application server with Uvicorn workers
CMD ["gunicorn", "app.main:app", "--workers", "1", "--worker-class", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000"]


