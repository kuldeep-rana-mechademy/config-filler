FROM python:3.12.9-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv (universal package manager)
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.cargo/bin:$PATH"

# Copy pyproject.toml and lock files (if any)
COPY pyproject.toml ./

# Sync dependencies using uv
RUN uv sync --no-dev

# Copy all application files
COPY . /app/

# Set the entrypoint to your application
CMD ["uv", "run", "python", "-m", "main"]