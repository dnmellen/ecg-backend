# ECG Backend

[![Run Tests](https://github.com/dnmellen/ecg-backend/actions/workflows/tests.yml/badge.svg)](https://github.com/dnmellen/ecg-backend/actions/workflows/tests.yml)

## Quickstart

### Prerequisites

- Docker

### Running the application

Notice that the `.env.docker` file is used to set the environment variables for the application in **development**. You can change the values in this file to suit your needs.

To run the application, execute the following command:

```bash
docker compose up -d
```

This will start the application and the database. The application will be available at `http://localhost:8000`.

### Create admin user

Creating an admin user is necessary to create other users. To create an admin user, execute the following command:

```bash
scripts/create_admin_user.sh admin
```

### Run the api as a development server in foreground

This way of running the application is useful for development. It will start the application in the foreground and you will be able to see the logs in the terminal.

```bash
docker-compose run --rm --service-ports api
```