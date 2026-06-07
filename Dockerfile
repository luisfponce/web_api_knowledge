FROM python:3.12-slim

# Environment hygiene
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# System deps first (layer caching)
RUN apt-get update \
 && apt-get install -y --no-install-recommends \
    build-essential \
    libmariadb-dev \
    mariadb-client \
    curl \
 && rm -rf /var/lib/apt/lists/*

# Set a non-root working directory
WORKDIR /app

# Install Python deps separately for caching
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
 && pip install --no-cache-dir -r requirements.txt \
 && python -c "import site; from pathlib import Path; paths = [Path(p) / 'fastapi_mail' / 'config.py' for p in site.getsitepackages()]; path = next(p for p in paths if p.exists()); text = path.read_text(); text = text.replace('from pydantic import FilePath, DirectoryPath, EmailStr, conint', 'from pydantic import FilePath, DirectoryPath, EmailStr, SecretStr, conint'); path.write_text(text)"

# Copy application code last
COPY webapi/ .

# Runtime contract
EXPOSE 8000

# Healthcheck (FastAPI root or /health endpoint)
HEALTHCHECK --interval=10s --timeout=2s --retries=5 \
  CMD curl -f http://127.0.0.1:8000 || exit 1

# Start app
CMD ["uvicorn", "main:myapp", "--host", "0.0.0.0", "--port", "8000"]
