# syntax=docker/dockerfile:1.4

#########################
# Base Builder Image
#########################
FROM --platform=$BUILDPLATFORM python:3.10-alpine AS builder

WORKDIR /code

# Install dependencies
COPY requirements.txt /code
RUN --mount=type=cache,target=/root/.cache/pip \
    pip3 install --no-cache-dir -r requirements.txt

# Copy entire app
COPY . /code

#########################
# Development Environment
#########################
FROM builder AS dev-envs

RUN apk update && apk add --no-cache git bash

RUN addgroup -S docker && \
    adduser -S --shell /bin/bash --ingroup docker vscode

# Set default app run command
CMD ["python3", "app.py"]

#########################
# Testing Environment
#########################
FROM builder AS test-env

# Install pytest for running tests
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --no-cache-dir pytest

# Default command to run tests
CMD ["pytest", "--maxfail=1", "--disable-warnings", "-q"]
