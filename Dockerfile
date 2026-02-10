FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /
RUN apt-get update && apt-get install -y --no-install-recommends build-essential libmariadb-dev mariadb-client \
  && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install -U fastapi-mail
COPY webapi ./

EXPOSE 8000

CMD ["uvicorn", "main:myapp", "--host", "0.0.0.0", "--port", "8000"]
