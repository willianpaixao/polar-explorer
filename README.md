# Polar Exporter

[![pipeline status](https://gitlab.com/willianpaixao/polar-explorer/badges/master/pipeline.svg)](https://gitlab.com/willianpaixao/polar-explorer/commits/master)
[![coverage report](https://gitlab.com/willianpaixao/polar-explorer/badges/master/coverage.svg)](https://gitlab.com/willianpaixao/polar-explorer/commits/master)

An experimental project to extract data from [Polar Accesslink API](https://www.polar.com/accesslink-api), store locally and allow plot dashboards.

## Getting Started
#### Polar Flow
Well, it goes without saying that you need to have a Polar device and an account at [Polar Flow](https://flow.polar.com).
Once you start generating data, you need to [register a new client application](https://admin.polaraccesslink.com) in order to get API keys and proceed fetching the data from Accesslink API.

#### SECRETS_FILE
Then you will need to provide the keys in a file inside of the instance folder. [\[1\]](https://flask.palletsprojects.com/en/1.1.x/config/#instance-folders)

An optional `SECRET_KEY` will improve your application's security. [\[2\]](https://flask.palletsprojects.com/en/1.1.x/config/#SECRET_KEY)

The following example of `SECRETS_FILE`:
``` python
CLIENT_ID="f3e94f75-3191-4999-9af2-7320c16a796e"
CLIENT_SECRET="73d6dd0f-9d45-4874-9179-6a35321920a5"
```

> NOTE: if you fail to properly pass an env file, the following error will appear in the logs: `ERROR: Secret file not provided, aborting...`.

> NOTE: a lazy way to generate a `SECRET_KEY` for Flask is by simply running `python -c 'import uuid; print(uuid.uuid4());'`.

#### Setting up the environment
> NOTE: We assume you have [Pipenv](https://pipenv-fork.readthedocs.io/en/latest) installed.

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
FLASK_ENV=testing SECRETS_FILE=secrets.env.sample pytest --setup-show
```
