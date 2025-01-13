FROM --platform=linux/amd64 python:3.12-slim

RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    unzip \
    postgresql \
    libpq-dev \
    software-properties-common \
    && rm -rf /var/lib/apt/lists/*

RUN curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
RUN unzip awscliv2.zip
RUN ./aws/install

# poetry install steps
RUN pip install poetry==1.7.1

ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache

WORKDIR /app

COPY pyproject.toml poetry.lock ./
RUN touch README.md

ENV AWS_DEFAULT_REGION="us-east-1"
RUN poetry install --no-root

# bring in full app and install
COPY streamlit/ /app/

RUN poetry install --no-root