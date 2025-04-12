## Setup Using Docker
A quicker way of running ACC II locally is to use `docker compose`. This will start up 3 containers for API, web and database.

### Start
Use `-d` if you want the containers to start in the background.

```bash 
$ docker compose up -d
```

### Stop
```bash
$ docker compose down
```

### Production startup
In order to run compose in production mode, you need to specify which compose files should be used:

```bash
$ docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

*Notes*: 
- This will not work locally as the frontend app will try to make requests to the production server.
- Environment variable `PROD_DB_PASSWORD` needs to be specified (any password).

### Compose Files
- `docker-compose.yml` base configuration.
- `docker-compose.override.yml` development configuration. Is used automatically.
- `docker-compose.prod.yml` production configuration. Needs to be explicitly specified (as described above)