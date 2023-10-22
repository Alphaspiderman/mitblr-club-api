
# MIT-BLR Club API

An API to interface with the backend database containing information for operating the club ecosystem

We strongly recommend that clubs contribute to the repository with the features (as issues or PRs) they require instead of forking and hosting a custom instance as it will lead to fragmentation.
## Getting Started (Running Locally)

### Prerequisites

- Git: You need Git to clone the project.
- Python: You need Python to run the project.
- Python Poetry: You need Poetry as a dependency manager.

### Clone the Project

```bash
git clone https://github.com/Alphaspiderman/mitblr-club-api.git
```

### Navigate to the Project Directory

```bash
cd mitblr-club-api
```

### Install Dependencies

Install Poetry if you haven't already 

```bash
pip install poetry
```

Then use it to install project dependencies.

```bash
poetry install
```

### Setup Environment Variables
Following the desciriptions provided in the "Environment Variables" section setup the .env file

### Start the server

```bash
  poetry run task server
```


## Environment Variables

Make sure to set the following environment variables in your `.env` file:

- `MONGO_CONNECTION_URI`: The connection URI for the MongoDB server.
- `IS_PROD`: Determines the database connection and toggles `auto-reload` and `debug` in Sanic.
- `SORT_YEAR`: Sets the sorting year for event documents in the database.
- `HOST`: Used to add information about where the JWT was issued from, in case of multiple API instances.
## Deployment (Production)

The following section is only for reference for those interested in learning about the process. 

To deploy this project to production, follow these steps:

### Clone the Project

```bash
git clone https://github.com/Alphaspiderman/mitblr-club-api.git
```

### Navigate to the Project Directory

```bash
cd mitblr-club-api
```

### Build the Docker Image

```bash
docker build . -t clubapi
```

### Configure the ENV File

Create and configure your `.env` file.

### Generate a Public and Private RSA Key Pair

Generate a public and private RSA key pair if necessary.

### Run the Container

Run the Docker container to deploy the project.

```bash
docker run -d --name clubapi -v private-key.pem:/app/private-key.pem:ro -v public-key.pem:/app/public-key.pem:ro -v .env:/app/.env:ro -p 80:8000 clubapi:latest
```

Note:
We do not include the RSA keys or the `.env` file in the Docker container itself; instead, we mount them. This is to prevent accidently shipping with the container image

That's it! You've successfully deployed the MIT-BLR Club API in a production environment.
## Contributing

Contributions are always welcome!

Do contact the current project maintainers beforehand for more information relating to the project.


## Documentation
### API
[API Documentation](https://api.mitblr.club/docs)

### Reference
[Motor (MongoDB AsyncIO Driver)](https://motor.readthedocs.io/en/stable/)

[Sanic (Guide)](https://sanic.dev/en/guide/)

[Sanic (Documentation)](https://sanic.readthedocs.io/en/stable/sanic/api_reference.html)

[OpenAPI Spec](https://spec.openapis.org/oas/v3.1.0)
