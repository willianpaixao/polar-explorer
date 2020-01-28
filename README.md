# Polar Exporter

[![pipeline status](https://gitlab.com/willianpaixao/polar-explorer/badges/master/pipeline.svg)](https://gitlab.com/willianpaixao/polar-explorer/commits/master)
[![coverage report](https://gitlab.com/willianpaixao/polar-explorer/badges/master/coverage.svg)](https://gitlab.com/willianpaixao/polar-explorer/commits/master)

An experimental project to extract data from [Polar Accesslink API](https://www.polar.com/accesslink-api), store locally and allow plot dashboards.

## Getting Started

#### SECRETS_FILE
You need to provide a file containing the API key and secret if you want to make calls to the Polar API.

> If you fail to properly pass an env file, the following error will appear in the logs: `ERROR: Secret file not provided, aborting...`.

> NOTE: a lazy way to generate a `SECRET_KEY` for Flask is by simply running `python -c 'import uuid; print(uuid.uuid4());'`.

#### Setting up the environment
> NOTE: We assume you have [Pipenv](https://pipenv-fork.readthedocs.io/en/latest/) installed.

``` bash
$ pipenv install --dev && pipenv shell
```

#### Running in the command line
``` bash
$ FLASK_ENV=development flask run
```
## Development
Before committing your code, please install the pre-commit hooks and test them:
``` bash
pre-commit install && pre-commit run --all
```

## Testing
You can run the unit tests by running:
``` bash
$ FLASK_ENV=testing pytest
```
