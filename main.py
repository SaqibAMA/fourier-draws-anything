from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from fourier import fourier_coefficients, resample_closed_path, series_value_at

SAMPLES = 500
MAX_DEPTH = SAMPLES // 2

app = FastAPI()


class FitRequest(BaseModel):
    points: list[tuple[float, float]] = Field(min_length=2)
    depth: int = Field(ge=0, le=MAX_DEPTH)


class Coefficients(BaseModel):
    a0: float
    a: list[float]
    b: list[float]


class FitResponse(BaseModel):
    period: int
    x: list[float]
    y: list[float]
    x_coefficients: Coefficients
    y_coefficients: Coefficients


def fit_coordinate(samples, depth):
    a0, a_list, b_list = fourier_coefficients(samples, depth)
    values = [series_value_at(t, len(samples), a0, a_list, b_list) for t in range(len(samples))]
    return values, Coefficients(a0=a0, a=a_list, b=b_list)


@app.post("/api/fit")
def fit(request: FitRequest) -> FitResponse:
    """Closed-loop Fourier fit of the drawn path; x and y are each fitted separately at the given depth."""
    path = resample_closed_path(request.points, SAMPLES)
    if path is None:
        raise HTTPException(status_code=422, detail="Drawing has no length")

    x_values, x_coefficients = fit_coordinate([x for x, y in path], request.depth)
    y_values, y_coefficients = fit_coordinate([y for x, y in path], request.depth)
    return FitResponse(
        period=SAMPLES, x=x_values, y=y_values,
        x_coefficients=x_coefficients, y_coefficients=y_coefficients,
    )


app.mount("/", StaticFiles(directory="static", html=True))
