FROM ubuntu:20.04
ENV DEBIAN_FRONTEND=noninteractive

# Update and install dependencies, Java (for Elasticsearch/Logstash), PostgreSQL, and Supervisor.
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    apt-transport-https \
    software-properties-common \
    openjdk-11-jdk \
    supervisor \
    postgresql postgresql-contrib \
    curl \
    dos2unix

# Create PostgreSQL data directory and set proper ownership.
RUN mkdir -p /var/lib/postgresql/12/main && chown -R postgres:postgres /var/lib/postgresql/12/main

# Add Elastic GPG key and repository, then install Elasticsearch and Logstash.
RUN wget -qO - https://artifacts.elastic.co/GPG-KEY-elasticsearch | apt-key add - && \
    apt-get install -y apt-transport-https && \
    echo "deb https://artifacts.elastic.co/packages/7.x/apt stable main" | tee -a /etc/apt/sources.list.d/elastic-7.x.list && \
    apt-get update && \
    apt-get install -y elasticsearch logstash

# Download the PostgreSQL JDBC driver (adjust version as needed)
RUN wget -qO /usr/share/java/postgresql.jar https://jdbc.postgresql.org/download/postgresql-42.5.1.jar

# Configure Elasticsearch (e.g. set cluster name and bind to all interfaces)
RUN sed -i 's/#cluster.name: my-application/cluster.name: docker-cluster/' /etc/elasticsearch/elasticsearch.yml && \
    sed -i 's/#network.host: 192.168.0.1/network.host: 0.0.0.0/' /etc/elasticsearch/elasticsearch.yml

# Copy Supervisor configuration file.
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Copy Logstash configuration file.
COPY logstash.conf /etc/logstash/conf.d/logstash.conf

# Copy PostgreSQL configuration file.
COPY postgresql.conf /var/lib/postgresql/12/main/postgresql.conf
COPY etcpostgresql.conf /etc/postgresql/12/main/postgresql.conf
COPY etcpg_hba.conf /etc/postgresql/12/main/pg_hba.conf

# Copy Elasticsearch config file.
COPY elasticsearch.yml /etc/elasticsearch/elasticsearch.yml

# Copy entrypoint script (which will initialize PostgreSQL and create the Records table).
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh && dos2unix /entrypoint.sh

# Expose PostgreSQL (5432) and Elasticsearch (9200) ports.
EXPOSE 5432 9200

# Use the entrypoint script to initialize the database and start Supervisor.
ENTRYPOINT ["/entrypoint.sh"]

# docker build -t multi-service-stack .
# docker run -p 5432:5432 -p 9200:9200 multi-service-stack
