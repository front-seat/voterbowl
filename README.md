# voterbowl

Prepare for the ultimate showcase showdown.
https://voterbowl.org/

We use:

- [Python 3.12](https://www.python.org/)
- [Django 5](https://www.djangoproject.com/)
- [Postgres 16](https://www.postgresql.org/)

We spend all our hipster tech tokens for this project to help us build a front-end directly in Django-land. In particular, we use:

- [HTMX](https://htmx.org/) with [django-htmx](https://github.com/adamchainz/django-htmx)
- [css-scope-inline](https://github.com/gnat/css-scope-inline)
- [surreal](https://github.com/gnat/surreal?tab=readme-ov-file)

Having never used any of these toys before, we'll see how this pans out.

(Others under consideration include [django-slippers](https://github.com/mixxorz/slippers), [django-template-partials](https://github.com/carltongibson/django-template-partials), and [django-components](https://github.com/EmilStenstrom/django-components).)

For code cleanliness, we also use:

- [Ruff](https://github.com/astral-sh/ruff) for linting
- [mypy](https://mypy-lang.org/) for type checking

### Getting a local dev instance running

1. Make sure you have python 3.12 installed
1. Create and enable a python virtualenv with `python -m venv .venv; source .venv/bin/activate`
1. Install the python dependencies with `pip install -r requirements.txt` or `pip install ".[dev]"`
1. Get postgres set up. If you've got docker installed, `./scripts/dockerpg.sh up`
1. Configure your environment variables. (See `.env.sample` and `settings.py`)
1. Run the app. `./manage.py runserver` and visit http://localhost:8000/
