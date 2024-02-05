# ECG Backend

[![Run Tests](https://github.com/dnmellen/ecg-backend/actions/workflows/tests.yml/badge.svg)](https://github.com/dnmellen/ecg-backend/actions/workflows/tests.yml)

## Quickstart

### Prerequisites

- Docker & Docker Compose

### Running the application

Notice that the `.env.docker` file is used to set the environment variables for the application in **development**. You can change the values in this file to suit your needs.

To run the application, execute the following command:

```bash
./run_dev.sh
```

This will start the application and the database. The application will be available at `http://localhost:8000`.

### Run the api as a development server in foreground

This way of running the application is useful for development. It will start the application in the foreground and you will be able to see the logs in the terminal.

```bash
docker-compose run --rm --service-ports api
```

## Documentation

- API Docs: [http://localhost:8000/docs](http://localhost:8000/docs).
- Project documentation: ???.