FROM debian:bookworm-slim AS c-builder
RUN apt-get update && apt-get install -y --no-install-recommends gcc libc6-dev

WORKDIR /build
# Copy your C source code (assuming it's named 'count_files.c' in your context)
COPY fast_ls.c .
RUN gcc -O3 -o fast_ls fast_ls.c

# -----------------------------------------------------------

FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim AS builder
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy

WORKDIR /app
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --locked --no-install-project --no-dev

COPY . /app
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-dev

# -----------------------------------------------------------

FROM python:3.12-slim-bookworm

# Setup a non-root user
RUN groupadd --system --gid 999 nonroot \
 && useradd --system --gid 999 --uid 999 --create-home nonroot

 # Copy the application from the builder
COPY --from=builder --chown=nonroot:nonroot /app /app
COPY --from=c-builder /build/fast_ls /usr/local/bin/fast_ls

# Place executables in the environment at the front of the path
ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONUNBUFFERED=1
# Use the non-root user to run our application
USER nonroot

# Use `/app` as the working directory
WORKDIR /app

# Run the FastAPI application by default
CMD ["python", "src/main.py"]