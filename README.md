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

This will start the application and the database. The application will be available at [http://localhost:8000/api/docs](http://localhost:8000/api/docs).

## Documentation

- API Docs: [http://localhost:8000/api/docs](http://localhost:8000/api/docs).
- Project documentation: [https://dnmellen.github.io/ecg-backend/](https://dnmellen.github.io/ecg-backend/).
