# Another FastAPI Starter Project

## Dev Setup

Init project (dev, CI)
```sh
$ cd fastapi-async-starter
# Create a virtual environment for development (recommend virtualenv and pyenv)
$ virtualenv .venv -p ~/.pyenv/versions/3.12.1/bin/python
$ source .venv/bin/activate
# Copy the environment defaults and edit as you please
$ cp .env.example .env
# Ensure Poetry puts the virtual environment in your project folder (will be ignored by git)
$ poetry config virtualenvs.in-project true
$ poetry install --with dev
$ docker network create app_network
$ docker compose up --build
```

Init project (prod)
```sh
$ cd fastapi-async-starter
$ poetry install --without dev
```

### Alembic Migrations

- Create new auto migrations
```shell
docker compose exec app makemigrations
```

- Run migrations
```shell
docker compose exec app migrate
```

- Downgrade migrations
```shell
docker compose exec app downgrade -1  # or -2 or base or hash of the migration
```
