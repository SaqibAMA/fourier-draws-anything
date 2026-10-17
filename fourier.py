import numpy as np


def coefficient(samples, period, wave_function, n):
    """(2 / T) * integral of samples(t) * wave(2*pi*n*t / T) dt, as a rectangle sum with dt = 1."""
    t = np.arange(len(samples))
    wave_values = wave_function(2 * np.pi * n * t / period)
    return (2 / period) * np.sum(samples * wave_values)


def fourier_coefficients(samples, depth):
    """Returns (a0, a_list, b_list); a_list[i] and b_list[i] belong to n = i + 1."""
    period = len(samples)

    a0 = (2 / period) * np.sum(samples)
    a_list = []
    b_list = []
    for n in range(1, depth + 1):
        a_list.append(coefficient(samples, period, np.cos, n))
        b_list.append(coefficient(samples, period, np.sin, n))

    return a0, a_list, b_list


def series_value_at(t, period, a0, a_list, b_list):
    """f(t) = a0/2 + sum over n of (a_n * cos(2*pi*n*t / T) + b_n * sin(2*pi*n*t / T))."""
    total = a0 / 2
    for i in range(len(a_list)):
        n = i + 1
        total += a_list[i] * np.cos(2 * np.pi * n * t / period)
        total += b_list[i] * np.sin(2 * np.pi * n * t / period)
    return total


def fourier_approximation(samples, depth):
    """Returns the depth-N series evaluated at every sample position t = 0 .. T-1."""
    samples = np.asarray(samples, dtype=float)
    period = len(samples)
    a0, a_list, b_list = fourier_coefficients(samples, depth)
    return np.array([series_value_at(t, period, a0, a_list, b_list) for t in range(period)])


def path_length(points):
    return sum(np.hypot(b[0] - a[0], b[1] - a[1]) for a, b in zip(points, points[1:]))


def make_loop(points, closed_gap_fraction=0.05):
    """Returns a loop starting and ending at points[0].

    If the end is within closed_gap_fraction of the path length from the start, the path is
    treated as already closed. Otherwise it is retraced backwards so an open stroke becomes
    out-and-back along itself.
    """
    points = list(points)
    gap = np.hypot(points[-1][0] - points[0][0], points[-1][1] - points[0][1])
    if gap <= closed_gap_fraction * path_length(points):
        return points + [points[0]]
    return points + points[-2:0:-1] + [points[0]]


def resample_closed_path(points, count):
    """Returns count points spaced evenly along the loop made by make_loop(points).

    Returns None if every point is identical.
    """
    closed = make_loop(points)

    distance_at_point = [0.0]
    for i in range(1, len(closed)):
        step = np.hypot(closed[i][0] - closed[i - 1][0], closed[i][1] - closed[i - 1][1])
        distance_at_point.append(distance_at_point[-1] + step)

    total_length = distance_at_point[-1]
    if total_length == 0:
        return None

    resampled = []
    segment = 1
    for k in range(count):
        target = total_length * k / count
        while distance_at_point[segment] < target:
            segment += 1
        segment_length = distance_at_point[segment] - distance_at_point[segment - 1]
        fraction = (target - distance_at_point[segment - 1]) / segment_length if segment_length else 0
        x = closed[segment - 1][0] + fraction * (closed[segment][0] - closed[segment - 1][0])
        y = closed[segment - 1][1] + fraction * (closed[segment][1] - closed[segment - 1][1])
        resampled.append((x, y))
    return resampled
