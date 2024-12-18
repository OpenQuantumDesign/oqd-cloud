FROM python:3.10.13-slim-bookworm as build


RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y --no-install-recommends build-essential gcc && \
    apt-get install -y git  # for installing directly from git

ARG PIP_DISABLE_PIP_VERSION_CHECK=1
ARG PIP_NO_CACHE_DIR=1

WORKDIR /python

RUN python -m venv /python/venv

ENV PATH="/python/venv/bin:$PATH"

COPY docker/requirements.txt .
RUN pip install -r requirements.txt

RUN pip install oqd-compiler-infrastructure
RUN pip install oqd-core
RUN pip install oqd-analog-emulator


########################################################################################

FROM python:3.10.13-slim-bookworm as app

RUN apt update && \
    apt install -y --no-install-recommends supervisor && \
    apt-get install -y gcc g++  # needed from Cython


ARG PIP_DISABLE_PIP_VERSION_CHECK=1
ARG PIP_NO_CACHE_DIR=1

COPY --from=build /python/venv /python/venv

ENV PATH="/python/venv/bin:$PATH"
ENV PYTHONPATH="/app/src"

COPY . ./app
WORKDIR /app
RUN pip install .
#RUN pip install .[all]

#COPY ./supervisord.conf /etc/supervisor/conf.d/supervisord.conf
COPY ./docker/supervisord.conf /etc/supervisor/conf.d/supervisord.conf
CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]

########################################################################################

# RUN \
#     apt update \
#     && apt install wget -y \
#     && wget https://julialang-s3.julialang.org/bin/linux/x64/1.9/julia-1.9.3-linux-x86_64.tar.gz -P /opt \
#     && tar zxvf /opt/julia-1.9.3-linux-x86_64.tar.gz -C /opt 

# ENV PATH "$PATH:/opt/julia-1.9.3/bin"

# RUN julia -e 'using Pkg; Pkg.add(["QuantumOptics", "Configurations", "StatsBase", "DataStructures", "JSON3", "IonSim"])'
