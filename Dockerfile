# For more information, please refer to https://aka.ms/vscode-docker-python
FROM python:3-slim

RUN pip install uv

# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE=1

# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED=1

ENV CFBD__API_TOKEN=football_ranking

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

#  echo "MY_VAR=$MY_VAR" > /app/.env # Example: writes MY_VAR to /app/.env
# Copy the .env file to the container
COPY .env /app/.env

# write to env file
RUN echo "CFBD__API_TOKEN=$CFBD__API_TOKEN" >> /app/.env

# Install pip requirements
COPY requirements.lock .
# RUN python -m pip install -r requirements.lock
RUN uv pip install --no-cache --system -r requirements.lock
# RUN uv sync --frozen

# Creates a non-root user with an explicit UID and adds permission to access the /app folder
# For more info, please refer to https://aka.ms/vscode-docker-python-configure-containers
RUN adduser -u 5678 --disabled-password --gecos "" appuser && chown -R appuser /app
USER appuser

# Make port available to the world outside this container
EXPOSE 8001

# During debugging, this entry point will be overridden. For more information, please refer to https://aka.ms/vscode-docker-python-debug
CMD ["python", "-m", "football_ranking"]
