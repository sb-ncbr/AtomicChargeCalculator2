# TODO: figure out a better way of doing this
# build stage is borrowed from https://github.com/sb-ncbr/ChargeFW2/blob/master/Dockerfile
FROM ubuntu:24.04 AS build

ARG DEPS="\
        ca-certificates \
        cmake \
        make \
        g++ \
        gemmi \
        gemmi-dev \
        git \
        libboost-program-options-dev \
        libeigen3-dev \
        libfmt-dev \
        libnanoflann-dev \
        libomp-dev \
        libstb-dev \
        nlohmann-json3-dev \
        zlib1g-dev \
        tao-pegtl-dev \
        python3-pybind11"

RUN apt-get update && \
    apt-get install -y --no-install-recommends ${DEPS} && \
    apt-get clean && rm -rf /var/lib/apt/lists*

RUN git clone -b development --depth 1 https://github.com/pilatmartin/ChargeFW2.git && \
        cd ChargeFW2 && \
        mkdir build && \
        cd build && \
        cmake .. -DCMAKE_INSTALL_PREFIX=. -DPYTHON_MODULE=ON && \
        make -j$(nproc) && \
        make install

# Bundle dependencies
RUN mkdir /dependencies /build
RUN mv /ChargeFW2/build/bin \
        /ChargeFW2/build/lib \
        /ChargeFW2/build/share \
        /build && \
    mv /usr/lib/x86_64-linux-gnu/libgomp.so.1*\
        /usr/lib/x86_64-linux-gnu/libfmt.so* \
        /usr/lib/x86_64-linux-gnu/libboost_program_options.so* \
        /dependencies

FROM ubuntu:24.04 AS app

# Set environment variables
ENV CHARGEFW2_DIR=/ChargeFW2/build
ENV PYTHONPATH=${CHARGEFW2_DIR}/lib
ENV POETRY_HOME=/opt/poetry
ENV POETRY_VIRTUALENVS_CREATE=false
ENV PATH="/opt/poetry/bin:$PATH"

# Install runtime dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        ca-certificates \
        curl \
        gcc \
        python3-dev \
        libpq-dev && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | python3 - && \
    poetry config virtualenvs.create false

# Copy over the build artifacts
COPY --from=build /build/ /${CHARGEFW2_DIR}
COPY --from=build /dependencies/* /usr/lib/x86_64-linux-gnu/

# Copy project files
WORKDIR /acc2
COPY poetry.lock pyproject.toml ./
RUN poetry install --no-interaction --no-ansi
COPY ./app /acc2/app

WORKDIR /acc2/app

CMD ["gunicorn", "--workers", "2", "--worker-class", "uvicorn.workers.UvicornWorker", "--timeout", "600", "--bind", "0.0.0.0:8000", "main:web_app"]