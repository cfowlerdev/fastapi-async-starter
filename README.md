# Another FastAPI Starter Project

NOTE: Work in Progress

## Dev Setup

Init project (dev, CI)
```sh
$ cd fastapi-starter
# Ensure Poetry puts the virtual environment in your project folder (will be ignored by git)
$ poetry config virtualenvs.in-project true
$ poetry install --with dev
$ docker network create app_network
$ docker-compose up --build
```

Init project (prod)
```sh
$ cd eventsapp-be-py
$ poetry install --without dev
```

Not currently using Poetry in the Dockerfile, so in the meantime relying on requirements.txt. This can be synced with Poetry by running the following:
```sh
$ poetry export -f requirements.txt --output requirements.txt --without-hashes
```
