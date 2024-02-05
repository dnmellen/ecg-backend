# Setup with Docker

This application runs in a Docker container. Docker compose is used to manage the services.

A quick startup script was created to handle all the necessary steps to run the application. The script is called `run_dev.sh` and is located in the root of the project.

To run the application, execute the following command:

```bash
./run_dev.sh
```

Follow the instructions, you will be asked to set a superuser password for the API.

The application will be available at [http://localhost:8000/api/docs](http://localhost:8000/api/docs).

## Destroy the dev environment

To destroy the dev environment, execute the following command:

```bash
scripts/destroy_environment.sh
```

This command will stop and remove the containers, networks, volumes, and images created by the `run_dev.sh` script.
