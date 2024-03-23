#!/bin/bash

# Squash and recreate all migrations (only useful in early dev)
rm -rf server/schools/migrations
python manage.py makemigrations schools
