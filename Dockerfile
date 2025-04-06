# Use an official lightweight Python image.
FROM python:3.11-slim

# Set the working directory in the container.
WORKDIR /app

# Copy the requirements file and install dependencies.
COPY ./site/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code.
COPY ./site .

# Expose port 5000 for the Flask app.
EXPOSE 5000

ARG ES_URL="http://host.docker.internal:9200"
ENV ELASTICSEARCH_URL=${ES_URL}

ARG PG_URL="host.docker.internal"
ENV POSTGRES_URL=${PG_URL}

ENV DEMO="TRUE"

# Run the Flask app.
CMD ["python", "main.py"]
