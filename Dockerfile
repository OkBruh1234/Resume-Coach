FROM python:3.13

COPY --from=ghcr.io/astral-sh/uv:0.12 /uv /bin/uv

ENV UV_PROJECT_ENVIRONMENT=/opt/venv UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy

WORKDIR /app

COPY pyproject.toml uv.lock .python-version ./

RUN uv sync --frozen --no-install-project --no-dev

COPY backend_fastapi/ .

ENV PATH="/opt/venv/bin:$PATH"

<<<<<<< Updated upstream
CMD ["sh", "-c", "alembic upgrade head && exec uvicorn main:app --host 0.0.0.0 --port 8080"]

# EXPOSE only documents the container port; use `docker run -p 8000:8080` to map host port 8000 to container port 8080.
EXPOSE 8080
=======
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8
>>>>>>> Stashed changes
