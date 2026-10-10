# For more information, please refer to https://aka.ms/vscode-docker-python
# Python is pinned: the uv.lock versions of pandas/scipy have no cp314 wheels,
# so a floating `python:3-slim` tag makes uv build them from source (no compiler).
FROM python:3.13-slim

# Keeps Python from generating .pyc files in the container, turns off buffering
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    CFBD__API_TOKEN=football_ranking \
    UV_LINK_MODE=copy

# uv is the project's package manager
RUN pip install --no-cache-dir uv

WORKDIR /app

# Dependencies first: this layer only rebuilds when the lockfile changes
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project

# Copy the application and install it into the same environment
COPY . /app
RUN uv sync --frozen --no-dev

# Use the project's virtual environment
ENV PATH="/app/.venv/bin:$PATH"

# Creates a non-root user with an explicit UID and adds permission to access the /app folder
# For more info, please refer to https://aka.ms/vscode-docker-python-configure-containers
RUN adduser -u 5678 --disabled-password --gecos "" appuser \
    && chown -R appuser:appuser /app
USER appuser

# Make port available to the world outside this container
EXPOSE 8001

# During debugging, this entry point will be overridden. For more information, please refer to https://aka.ms/vscode-docker-python-debug
CMD ["python", "-m", "football_ranking"]
