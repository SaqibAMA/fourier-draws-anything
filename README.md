# Fourier Draws Anything

Draw on the notebook-style canvas, then pick a depth N. The yellow curve is a Fourier series of that depth fitted to your drawing.

## Run

```
docker compose up --build
```

Open http://localhost:8000.

## Without Docker

```
uv run uvicorn main:app
```
