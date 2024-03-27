#!/bin/bash


export DATABASE_URL=postgres://${USER}:password@localhost:5432/postgres

# Run a local development server
python manage.py runserver
