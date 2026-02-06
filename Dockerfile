FROM python:3.9-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install system deps (needed for many python packages like psycopg2, pillow etc.)
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    gcc \
    git \
    curl \
    libpq-dev \
    libcurl4-openssl-dev \
    netcat-openbsd \
    && rm -rf /var/lib/apt/lists/*

# Install python deps
COPY requirements.txt .
COPY requirements_2026.txt .
COPY requirements_2023.txt .


RUN pip install --no-cache-dir -r requirements_2026.txt

COPY ./smallslive /app

COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

EXPOSE 8000

ENTRYPOINT ["/app/entrypoint.sh"]
# Run Django
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
