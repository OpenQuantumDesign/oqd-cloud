FROM python:3.12-slim-bookworm as build
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y --no-install-recommends build-essential gcc && \
    apt-get install -y git  # for installing directly from git 

WORKDIR /python
RUN uv venv /python/.venv
ENV PATH="/python/.venv/bin:$PATH"
COPY docker/requirements.txt .

RUN uv pip install -r requirements.txt

RUN uv pip install "oqd-analog-emulator@git+https://github.com/openquantumdesign/oqd-analog-emulator"
RUN uv pip install "oqd-trical@git+https://github.com/openquantumdesign/oqd-trical"

########################################################################################

FROM python:3.12-slim-bookworm as app
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

RUN apt update && \
    apt install -y --no-install-recommends supervisor && \
    apt-get install -y gcc g++  # needed from Cython

COPY --from=build /python/.venv /python/.venv

ENV PATH="/python/.venv/bin:$PATH"
ENV PYTHONPATH="/app/src"

COPY . ./app
WORKDIR /app
RUN uv pip install .[server]

# COPY ./supervisord.conf /etc/supervisor/conf.d/supervisord.conf
COPY ./docker/supervisord.conf /etc/supervisor/conf.d/supervisord.conf
CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]

########################################################################################