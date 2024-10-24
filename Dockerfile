# Dockerfile based on https://github.com/python-poetry/poetry/discussions/1879
# UV docker guide: https://docs.astral.sh/uv/guides/integration/docker/
# Example: https://github.com/astral-sh/uv-docker-example/blob/main/Dockerfile
# `python-base` sets up all our shared environment variables
FROM python:3.12-slim AS python-base
# Note: uv provides some pre-built docker images, we can just take those instead
# https://docs.astral.sh/uv/guides/integration/docker/#available-images
ENV PYTHONUNBUFFERED=1 \
    # Prevents python creating .pyc as files
    PYTHONDONTWRITEBYTECODE=1 \
    \
    # Pip
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    \
    # Paths
    # This is where our requirements + virtual environment will live
    PYSETUP_PATH="/opt/pysetup" \
    VENV_PATH="/opt/pysetup/.venv"

# Once project is installed, you can:
# a) "Activate" virtual environment by placing binary directory at the front of the path
# b) Or, you can use `uv run` for any commands that require the environment
# c) Or, `UV_PROJECT_ENVIRONMENT` setting can be set before syncing to install to
#    the system Python environment and skip environment activation entirely.
# Prepend venv to PATH
ENV PATH="$VENV_PATH/bin:$PATH"

# `builder-base` stage is used to build deps + create our virtual environment
FROM python-base AS builder-base
RUN apt-get update && apt-get install --no-install-recommends -y \
    # deps for downloading release archive (uv)
    curl ca-certificates \
    # deps for building python deps
    build-essential

# Install uv: https://docs.astral.sh/uv/guides/integration/docker/#installing-uv
# curl options: -s: silent, -S: but show errors if it fails, -L (--location)
# Download latest installer
# ADD https://astral.sh/uv/install.sh /uv-installer.sh
# Best practice is to pin to a specific uv version:
ADD https://astral.sh/uv/0.4.26/install.sh /uv-installer.sh
# Run installer then remove it
RUN sh /uv-installer.sh && rm /uv-installer.sh
# Alternatively, we can copy binary from pre-built image
# COPY --from=ghcr.io/astral-sh/uv:0.4.26 /uv /uvx /bin/
# Ensure the installed binary is on the PATH
ENV PATH="/root/.cargo/bin/:$PATH"

# Set working directory
WORKDIR $PYSETUP_PATH

# Install runtime dependencies
# Mount the required files directly, according to
# https://docs.astral.sh/uv/guides/integration/docker/
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-install-project
# --frozen: use the frozen lockfile

# `production` image used for runtime
FROM python-base AS production
COPY --from=builder-base $PYSETUP_PATH $PYSETUP_PATH
# WORKDIR /usr/src/simplecaptcha-bot
# COPY . /usr/src/simplecaptcha-bot
# If your project contains files that aren’t needed in final image
# (e.g., test files, docs), use `.dockerignore` file to keep image smaller.
ADD . /app
WORKDIR /app
# ADD is similar to COPY, but with more functionality:
# can automatically extract compressed files and download files from URLs.

# CMD defines the default command that runs when container starts from the image;
# does not create a new image layer; executed only when the container starts.
# CMD python -m app

# Typically, we want to tag the production image after building:
# `docker tag <image_id> myapp:latest`
# This is the image we would deploy or share.
# To manage disk space, we can run `docker image prune` to remove unused
# (i.e. untagged) images, including intermediate build images.
