# Atomic Charge Calculator II API

## Manual Setup

### Prerequisites
ACC II depends on the [ChargeFW2](https://github.com/sb-ncbr/ChargeFW2) python bindings. 

#### [Building ChargeFW2](https://github.com/sb-ncbr/ChargeFW2/tree/master?tab=readme-ov-file#installation)

*Note:* When running `cmake`, include `-DPYTHON_MODULE=ON` to generete python bindings:

```bash
$ cmake .. -DCMAKE_INSTALL_PREFIX=<WHERE-TO-INSTALL> -DPYTHON_MODULE=ON
```

#### [Using Python Bindings](https://github.com/sb-ncbr/ChargeFW2/blob/master/doc/ChargeFW2%20-%20tutorial.ipynb)

*Note:* `PYTHONPATH` environment variable is set in `app/.env` file. Overwrite it if you wish to install ChargeFW2 somewhere else.

### Startup Script
The remaining startup steps can be simplified using the `startup.sh` script:

```bash
$ ./startup.sh
```

### Installing Dependencies
ACC II uses [Poetry](https://python-poetry.org/) for depencency management.

#### Install Poetry
```bash
$ curl -sSL https://install.python-poetry.org | python3 -
```

#### Install Project Dependencies
*Note:* Poetry will automatically create a virtual environment inside the project before the installation.

```bash
$ poetry install
```

### Startup
We firstly need to start the database. Easiest way is by using an official postgresql docker image. Connection string is located in the `.env` file.
```bash
$ docker run -it --rm -e POSTGRES_PASSWORD=postgres -p 5432:5432 postgres:17-alpine
```

Following commands require being in the `app` directory:
```bash
$ cd app
```

After the database is ready, we need to run migrations:
```bash
$ poetry run alembic upgrade head
```

API can now be started just by running the main file:

```bash
$ poetry run gunicorn --workers 4 --worker-class uvicorn.workers.UvicornWorker main:web_app
```

API runs by default on `--bind 127.0.0.1:8000`. Documentation (Swagger) is available on `--bind 127.0.0.1:8000/docs`.
