FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim
WORKDIR /app
COPY pyproject.toml uv.lock .python-version ./
RUN uv sync --frozen --no-dev --no-install-project
COPY main.py fourier.py ./
COPY static ./static
EXPOSE 8000
CMD ["uv", "run", "--no-dev", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
