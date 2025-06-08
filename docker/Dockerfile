FROM python:3.12-slim-bookworm as build
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

RUN apt-get update && \
    apt-get upgrade -y && \
    apt install -y --no-install-recommends supervisor && \
    apt-get install -y git && \ 
    apt-get install -y gcc g++  # needed from Cython

COPY . ./app
ENV PYTHONPATH="/app/src"
WORKDIR /app

RUN uv venv
ENV PATH=".venv/bin:$PATH"

RUN uv pip install ".[server]"

COPY ./docker/supervisord.conf /etc/supervisor/conf.d/supervisord.conf
CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]

########################################################################################