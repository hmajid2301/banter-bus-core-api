ARG USERNAME=app
ARG USER_UID=1000
ARG USER_GID=1000

FROM python:3.10.5 as base

ARG USER_UID
ARG USER_GID
ARG USERNAME

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app \
    POETRY_VIRTUALENVS_IN_PROJECT=true

ENV PATH="/app/.venv/bin:$PATH"

RUN addgroup --gid $USER_GID --system app \
    && adduser --shell \
    /bin/false --disabled-password --uid $USER_UID --system --group $USERNAME


FROM base as builder

ARG POETRY_VERSION=1.1.13
ARG USERNAME

RUN apt-get update && \
    apt-get install -y make git build-essential sudo apt-transport-https && \
    echo $USERNAME ALL=\(root\) NOPASSWD:ALL > /etc/sudoers.d/$USERNAME \
    && chmod 0440 /etc/sudoers.d/$USERNAME && \
    pip install poetry==$POETRY_VERSION

WORKDIR /app
COPY poetry.lock pyproject.toml ./

RUN poetry install --no-dev


FROM builder as development

ENV BANTER_BUS_CORE_API_ENVIRONMENT=development

WORKDIR /app
RUN poetry install 
USER $USERNAME
COPY . .

EXPOSE 8080
CMD uvicorn --reload app:app --host $BANTER_BUS_CORE_API_WEB_HOST --port $BANTER_BUS_CORE_API_WEB_PORT


FROM python:3.10.5-slim as production

ENV BANTER_BUS_CORE_API_ENVIRONMENT=production

ARG USER_UID
ARG USER_GID
ARG USERNAME
ARG VENV_PATH="/app/.venv"

ENV PATH="$VENV_PATH/bin:$PATH"

RUN addgroup --gid $USER_GID --system app \
    && adduser --no-create-home --shell \
    /bin/false --disabled-password --uid $USER_UID --system --group $USERNAME

WORKDIR /app
USER $USERNAME
COPY --from=builder $VENV_PATH $VENV_PATH
COPY ./app /app/app

EXPOSE 8080
CMD uvicorn app:app --host $BANTER_BUS_CORE_API_WEB_HOST --port $BANTER_BUS_CORE_API_WEB_PORT
