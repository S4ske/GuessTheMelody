ARG PYTHON_VERSION=3.11
FROM python:${PYTHON_VERSION}-slim as base

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app
ENV DJANGO_SETTINGS_MODULE=guessthemelody.settings

WORKDIR /app

COPY . .
RUN python -m pip install uv && uv pip install --system .

CMD ["sh", "-c", "python manage.py migrate && daphne -b 0.0.0.0 -p 8000 --proxy-headers guessthemelody.asgi:application"]