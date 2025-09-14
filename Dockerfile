# Dockerfile
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install uv
RUN pip install uv

# Copy dependency files
COPY pyproject.toml .
COPY uv.lock* .

# Install dependencies using uv
RUN uv sync --frozen --no-dev

# Copy everything into container
COPY . .

