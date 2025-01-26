# Atomic Charge Calculator II

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
We firstly need to start the database. This can be simply achieved by using an official postgresql docker image. Connection string is located in `.env` file.
```bash
$ docker run -it --rm -e POSTGRES_PASSWORD=postgres -p 5432:5432 postgres:17-alpine
```


Application can now be started just by running the main file:

```bash
# development
$ poetry run fastapi dev app/main.py

# production
$ poetry run fastapi run app/main.py
```

Application runs by default on `localhost:8000`. Documentation (Swagger) is available on `localhost:8000/docs`.

## Docker
A quicker way of running ACC II is to use docker.

```bash 
# build image with name acc2
$ docker build -t acc2 .

# run container with name acc2-container
$ docker run --name acc2-container -p 8000:8000 acc2
```