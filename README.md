# voterbowl

The code behind https://voterbowl.org/

We use:

- [Python 3.12](https://www.python.org/)
- [Django 5](https://www.djangoproject.com/)
- [Postgres 16](https://www.postgresql.org/)

We spend all our hipster tech tokens for this project to help us build a front-end directly in Django-land. In particular, we use:

- [HTMX](https://htmx.org/) with [django-htmx](https://github.com/adamchainz/django-htmx)
- [htpy](https://htpy.dev/) for HTML building, rather than Django templates (with a small handful of exceptions).

So far, I'm liking both. For projects like this one, HTMX is a keeper. `htpy` has its advantages and its frictions; I'm reminded of javascript templating land just before JSX got introduced.

(Other hipster tools under consideration included [css-scope-inline](https://github.com/gnat/css-scope-inline) and [surreal](https://github.com/gnat/surreal?tab=readme-ov-file) for "locality of behavior", none of which turned out to be particularly desirable in practice; [django-slippers](https://github.com/mixxorz/slippers), [django-template-partials](https://github.com/carltongibson/django-template-partials), and [django-components](https://github.com/EmilStenstrom/django-components), all of which attempt to relieve pain points in Django's built-in templates but none of which seem terribly successful at it; and various bits of wisdom from [django-htmx-patterns](https://github.com/spookylukey/django-htmx-patterns/).)

For code cleanliness, we also use:

- [Ruff](https://github.com/astral-sh/ruff) for linting
- [mypy](https://mypy-lang.org/) for type checking

### Getting a local dev instance running

1. Make sure you have python 3.12 installed
1. Create and enable a python virtualenv with `python -m venv .venv; source .venv/bin/activate`
1. Install the python dependencies with `pip install -r requirements.txt`
1. Get postgres set up. If you've got docker installed, `./scripts/dockerpg.sh up`
1. Configure your environment variables. (See `.env.sample` and `settings.py`)
1. Run the app. `./scripts/runserver.sh` and visit http://localhost:8000/
