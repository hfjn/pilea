FROM python:3.8 AS build

RUN pip install poetry

RUN mkdir -p /pilea

WORKDIR /pilea

RUN poetry config "virtualenvs.create" "false"
COPY poetry.lock pyproject.toml /pilea/
RUN poetry install

COPY pilea/ /pilea/pilea
COPY README.md /pilea

RUN poetry build


FROM python:3.8-slim AS app

COPY --from=build /pilea/dist/*.whl /app/

RUN pip install /app/*.whl

RUN useradd -ms /bin/bash pilea

RUN mkdir -p /web

USER pilea:pilea

WORKDIR /web

ENTRYPOINT ["pilea"]