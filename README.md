Football Ranking

# FastAPI Project Template

A template repository for a FastAPI project that can automatically generate Unit files for easy project management using Systemd to start, restart, and stop the project.

# How to Use?

## 3. Sync the environment

```bash
# Set up the environment
# In a production environment, you can add --no-dev to all sync commands
# to reduce the installation of unnecessary dependencies
uv sync
```

## 4. Develop the project

```bash
# During development, try hot-reloading the project, which by default monitors all *.py files and .envs files
uv run dev
# Start the project
uv run start
```

First, define the necessary environment variables in the `AppConfig` and `UnicornConfig` in `config.py`, and provide default values. If you need to change the default values or if no default values are set, you need to define them in the `.env`.
