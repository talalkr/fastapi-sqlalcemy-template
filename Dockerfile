FROM python:3.14-alpine AS base

ENV PYTHONUNBUFFERED=1
ENV POETRY_HOME=/opt/poetry
ENV POETRY_VERSION=2.1.1
ENV PATH="$POETRY_HOME/bin:$PATH"
ENV PYTHONPATH="/app:${PYTHONPATH}"

WORKDIR /app

RUN mkdir -p /app/tests /app/utils $POETRY_HOME \
    && apk add --no-cache curl \
    && curl -sSL https://install.python-poetry.org | python3 - \
    && poetry config virtualenvs.create false

COPY poetry.lock pyproject.toml ./
COPY ./app ./app/
COPY ./tests ./tests/

RUN poetry install --verbose --no-root --without dev

EXPOSE 8000

FROM base AS test

WORKDIR /app
RUN poetry config virtualenvs.create false \
    && poetry install --no-root --with dev