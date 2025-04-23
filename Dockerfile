ARG PYTHON_VERSION=3.11
FROM python:${PYTHON_VERSION}-slim as base

ENV PYTHONDONTWRITEBYTECODE=1

ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH /app

WORKDIR /app

COPY . .

RUN python -m pip install uv

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev

RUN uv pip install --system .

EXPOSE 8000

CMD python manage.py migrate && python manage.py runserver 0.0.0.0:8000
