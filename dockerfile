FROM python:3.10-slim

# Install basic system dependencies
RUN apt-get update && apt-get install -y --fix-missing gcc mono-mcs make

# Install Poetry
RUN pip install poetry

# Set working folder
WORKDIR /app

# Copy the data
COPY . /app

# Expose the default sanic port
EXPOSE 8000

# Set entrypoint
ENTRYPOINT ["bash", "entrypoint.sh"]
