FROM python:3.11.1-alpine3.17

ARG GDAL_VERSION
ARG PYTHON_VERSION

RUN \
    apk update; \
    apk upgrade; \
    apk add --no-cache \
        bash \
        gfortran \
        cmake \
        g++ \
        git \
        gdal \
        gdal-dev \
        py3-numpy \
        py3-pip \
        openblas-dev \
        geos-dev \
    ;


COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

ENTRYPOINT ["bash"]