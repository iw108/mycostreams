
# The fiji builder
FROM debian:bullseye-slim as fiji-builder

RUN apt-get update && apt-get install -y \
        wget \
        unzip \
    && rm -rf /var/lib/apt/

# Retrieve ImageJ and source code
WORKDIR /opt/fiji

RUN wget https://downloads.imagej.net/fiji/latest/fiji-nojre.zip \
    && unzip fiji-nojre.zip \
    && rm fiji-nojre.zip \
    && rm Fiji.app/*.exe


# The builder image, used to build the virtual environment
FROM python:3.10-bullseye as builder

ENV POETRY_VERSION=1.4.2 \
    POETRY_HOME=/opt/poetry \
    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1 \
    POETRY_CACHE_DIR=/opt/.cache 

ENV PATH=$POETRY_HOME/bin:$PATH

RUN curl -sSL https://install.python-poetry.org | python3 - 

WORKDIR /app

COPY pyproject.toml poetry.lock ./

RUN poetry install --without dev --no-root && rm -rf $POETRY_CACHE_DIR


# The runtime image, used to just run the code provided its virtual environment
FROM python:3.10-slim-bullseye as runtime

ENV VENV_PATH=/app/.venv
ENV PATH=$VENV_PATH/bin:$PATH
ENV FIJI_HOME=/opt/fiji/Fiji.app

COPY --from=fiji-builder /opt/fiji/ opt/fiji
COPY --from=builder ${VENV_PATH} ${VENV_PATH}


RUN apt-get update && apt-get install -y \
        libjpeg-turbo-progs \
        libjpeg62-turbo-dev \ 
        libopenjp2-7-dev \
        maven \
        openjdk-11-jdk-headless \
    && rm -rf /var/lib/apt/


WORKDIR /app

COPY image_stitcher/ /app/image_stitcher/
COPY scripts /app/scripts

RUN ./scripts/startup.sh
