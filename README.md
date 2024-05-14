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
- [htpy](https://htpy.dev/) for HTML building, rather than Django templates (with a small handful of exceptions).

Having never used any of these toys before, we'll see how this pans out. (Update: I'm going to go back and remove `css-scope-inline` when I have a chance, in favor of, y'know, just being more careful with top-level CSS. `htpy` is better than Django templates for our purposes but not without its friction and pain.)

(Others under consideration include [surreal](https://github.com/gnat/surreal?tab=readme-ov-file), [django-slippers](https://github.com/mixxorz/slippers), [django-template-partials](https://github.com/carltongibson/django-template-partials), and [django-components](https://github.com/EmilStenstrom/django-components). And don't forget the [django-htmx-patterns](https://github.com/spookylukey/django-htmx-patterns/) documentation.)

For code cleanliness, we also use:

- [Ruff](https://github.com/astral-sh/ruff) for linting
- [mypy](https://mypy-lang.org/) for type checking

### Getting a local dev instance running

1. Make sure you have python 3.12 installed
1. Create and enable a python virtualenv with `python -m venv .venv; source .venv/bin/activate`
1. Install the python dependencies with `pip install -r requirements.txt`
1. Get postgres set up. If you've got docker installed, `./scripts/dockerpg.sh up`
1. Configure your environment variables. (See `.env.sample` and `settings.py`)
1. Run the app. `./manage.py runserver` and visit http://localhost:8000/
