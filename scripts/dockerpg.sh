#!/bin/bash

# Simple utility to start, stop, and reset a postgres docker instance.

# If you use this, you should set your DATABASE_URL to
# postgres://${USER}:password@localhost:5432/postgres

migrate() {
    # Run the wrapper script around django's migrate + superuser creation
    python manage.py migrate
}

createsuperuser() {
    if [ -z "$DJANGO_SUPERUSER_EMAIL" ]; then
      echo "DJANGO_SUPERUSER_EMAIL is not set. Will not create a superuser."
    else
      python manage.py createsuperuser --noinput
    fi
}

start() {
    # Start a docker container and spin up the database in a usable state
    docker run --name pg-voterbowl -p 5432:5432 -e POSTGRES_PASSWORD=password -e POSTGRES_USER=${USER} -d postgres:16
    # It takes a moment for the server to actually spin up
    sleep 5
    migrate
    createsuperuser
}

stop() {
    # Spin down the database and delete the docker instance
    docker stop pg-voterbowl
    docker rm pg-voterbowl
}

restart() {
    # Spin down the database, delete the docker instance, then spin up a new one
    stop
    start
}

resetdb() {
    # Drop the current database and clean it again
    PGPASSWORD=password dropdb --host=localhost --port=5432 --username=${USER} --no-password postgres
    PGPASSWORD=password createdb --host=localhost --port=5432 --username=${USER} --no-password postgres
    migrate
    createsuperuser
}

logs() {
    # Show postgres docker container logs
    docker logs pg-voterbowl
}

status() {
    # Show running postgres docker container process info, if any
    docker ps | grep pg-voterbowl
}


case "$1" in
     'start')
        start
        ;;
    'stop')
        stop
        ;;
    'restart')
        restart
        ;;
    'resetdb')
        resetdb
        ;;
    'logs')
        logs
        ;;
    'status')
        status
        ;;
    *)
        echo
        echo "Usage: $0 { start | stop | restart | resetdb | logs | status }"
        echo
        exit 1
esac

exit 0

