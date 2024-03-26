#!/bin/bash

# Squash and recreate all migrations (only useful in early dev)
rm -rf server/vb/migrations
python manage.py makemigrations vb
