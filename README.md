# MIT-BLR Club API

An API to interface with the backend database containing information for operating the club ecosystem

We strongly recommend that clubs contribute to the repository with the features (as issues or PRs) they require instead
of forking and hosting a custom instance as it will lead to fragmentation.

## Environment Variables

Make sure to set the following environment variables in your `.env` file:

- `MONGO_CONNECTION_URI`: The connection URI for the MongoDB server.
- `IS_PROD`: Determines the database connection and toggles `auto-reload` and `debug` in Sanic.
- `SORT_YEAR`: Used to categorise events by academic year. This is the year in which the academic year starts. For
  example, if the academic year starts in July 2023, then this value should be set to 2023.
- `HOST`: Used to add information about where the JWT was issued from, in case of multiple API instances.
- `PROXIES_COUNT`: Used to set the number of trusted proxies in the connection

In addition to the above, you will also need a public and private RSA key pair to sign and verify JWTs. The public key
will be used to verify the JWTs, and the private key will be used to sign them. The keys should be stored in the
project directory as `public-key.pem` and `private-key.pem` respectively.

It is to be noted that, in production, the private key should be kept secret and should not be shared with anyone. The
public key, however, can be shared with anyone who needs to verify the JWTs. Rotating the keys will lead to all existing JWTs becoming invalid.

For more information related to MongoDB Connection URIs, refer to the
[MongoDB Documentation](https://docs.mongodb.com/manual/reference/connection-string/).


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

Install Poetry if you haven't already.

```bash
pip install poetry
```

Then use it to install project dependencies.

```bash
poetry install
```

### Setup Environment Variables

Following the descriptions provided in the "Environment Variables" section set up the `.env` file.

### Generate a Public and Private RSA Key Pair

Generate a public and private RSA key pair if necessary.

### Start the server

```bash
  poetry run task server
```

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

Following the descriptions provided in the "Environment Variables" section set up the `.env` file.

### Generate a Public and Private RSA Key Pair

Generate a public and private RSA key pair if necessary.

### Run the Container

Run the Docker container to deploy the project.

```bash
docker run -d --name clubapi -v private-key.pem:/app/private-key.pem:ro -v public-key.pem:/app/public-key.pem:ro -v .env:/app/.env:ro -p 80:8000 clubapi:latest
```

Note:
We do not include the RSA keys or the `.env` file in the Docker container itself; instead, we mount them. This is to
prevent accidentally shipping with the container image.

That's it! You've successfully deployed the MIT-BLR Club API in a production environment.

## Contributing

Contributions are always welcome!

Do contact the current project maintainers beforehand for more information relating to the project.

## Documentation

### API

[API Documentation](https://api.mitblr.club/docs)

### References

- [Motor (MongoDB AsyncIO Driver)](https://motor.readthedocs.io/en/stable/)
- [Sanic (Guide)](https://sanic.dev/en/guide/)
- [Sanic (Documentation)](https://sanic.readthedocs.io/en/stable/sanic/api_reference.html)
- [OpenAPI Spec](https://spec.openapis.org/oas/v3.1.0)
