# Dockerfile from https://github.com/python-poetry/poetry/discussions/1879
# UV docker guide: https://docs.astral.sh/uv/guides/integration/docker/
# `python-base` sets up all our shared environment variables
FROM python:3.12-slim AS python-base
# Note: uv provides some pre-built docker images, we can just take those instead
# https://docs.astral.sh/uv/guides/integration/docker/#available-images
ENV PYTHONUNBUFFERED=1 \
    # prevents python creating .pyc as files
    PYTHONDONTWRITEBYTECODE=1 \
    \
    # pip
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    \
    # poetry
    # https://python-poetry.org/docs/configuration/#using-environment-variables
    # POETRY_VERSION=1.8.2 \
    # make poetry install to this location
    # POETRY_HOME="/opt/poetry" \
    # make poetry create the virtual environment in the project's root
    # it gets named `.venv`
    # POETRY_VIRTUALENVS_IN_PROJECT=true \
    # do not ask any interactive question
    # POETRY_NO_INTERACTION=1 \
    \
    # paths
    # this is where our requirements + virtual environment will live
    PYSETUP_PATH="/opt/pysetup" \
    VENV_PATH="/opt/pysetup/.venv"

# prepend poetry and venv to path
# ENV PATH="$POETRY_HOME/bin:$VENV_PATH/bin:$PATH"
ENV PATH="$VENV_PATH/bin:$PATH"

# `builder-base` stage is used to build deps + create our virtual environment
FROM python-base AS builder-base
RUN apt-get update && apt-get install --no-install-recommends -y \
    # deps for downloading release archive (uv)
    curl ca-certificates \
    # deps for building python deps
    build-essential

# install poetry - respects $POETRY_VERSION & $POETRY_HOME
# curl options:
# -s: silent
# -S: When used with -s, --silent, it makes curl show an error message if it fails
# -L, --location: If the server reports that requested page has moved to a different
# location, this option makes curl redo the request on the new place.
# RUN curl -sSL https://install.python-poetry.org | python -

# Install uv: https://docs.astral.sh/uv/guides/integration/docker/#installing-uv
# Download latest installer
# ADD https://astral.sh/uv/install.sh /uv-installer.sh
# Best practice is to pin to a specific uv version:
ADD https://astral.sh/uv/0.4.25/install.sh /uv-installer.sh
# Run installer then remove it
RUN sh /uv-installer.sh && rm /uv-installer.sh
# Ensure the installed binary is on the `PATH`
ENV PATH="/root/.cargo/bin/:$PATH"

# Copy project requirement files here to ensure they will be cached
# (Do we need to copy the whole project into the image?)
WORKDIR $PYSETUP_PATH
# COPY poetry.lock pyproject.toml ./

# Install runtime dependencies
# Poetry uses $POETRY_VIRTUALENVS_IN_PROJECT internally
# RUN poetry install --no-dev
# COPY uv.lock pyproject.toml ./
# We can mount the required files directly, according to
# https://docs.astral.sh/uv/guides/integration/docker/
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-install-project
# --frozen - to use the frozen lockfile

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
