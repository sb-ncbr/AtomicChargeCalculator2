FROM chargefw2-base:local

# Set environment variables
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

# Copy project files
WORKDIR /acc2
COPY poetry.lock pyproject.toml ./
RUN poetry install --no-interaction --no-ansi --no-root

COPY ./app /acc2/app
COPY ./entrypoint.sh /acc2/
RUN chmod +x /acc2/entrypoint.sh

ENTRYPOINT ["/acc2/entrypoint.sh"]