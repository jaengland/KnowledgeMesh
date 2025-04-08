#!/bin/bash
set -e

echo "Checking if PostgreSQL is initialized..."
if [ ! -f /var/lib/postgresql/12/main/PG_VERSION ]; then
  echo "Initializing PostgreSQL database..."
  su - postgres -c "/usr/lib/postgresql/12/bin/initdb -D /var/lib/postgresql/12/main"
fi

if [ ! -f /var/lib/postgresql/12/main/pg_hba.conf ]; then
  echo "Creating minimal pg_hba.conf..."
  cat <<EOF > /var/lib/postgresql/12/main/pg_hba.conf
# PostgreSQL Client Authentication Configuration File
# TYPE  DATABASE        USER            ADDRESS                 METHOD

# Local (Unix socket) connections:
local   all             all                                     trust

# IPv4 local connections:
host    all             all             127.0.0.1/32            trust
host    all             all             0.0.0.0/0               trust

EOF
fi

cp /etc/postgresql/12/main/pg_ident.conf /var/lib/postgresql/12/main/pg_ident.conf
chown postgres:postgres /var/lib/postgresql/12/main/*
chown postgres:postgres /etc/postgresql/12/main/*

# Ensure the log directory exists so PostgreSQL’s logging collector can write logs.
echo "Ensuring PostgreSQL log directory exists..."
mkdir -p /var/lib/postgresql/12/main/log
chown postgres:postgres /var/lib/postgresql/12/main/log

mkdir -p /var/run/postgresql
chown postgres:postgres /var/run/postgresql

#chown -R elasticsearch:elasticsearch /usr/share/elasticsearch/data
chown -R elasticsearch:elasticsearch /var/log/elasticsearch

# listen address * so that I can develop with local tools
echo "Starting temporary PostgreSQL server for initialization..."
su - postgres -c "/usr/lib/postgresql/12/bin/pg_ctl -t 1000 -D /var/lib/postgresql/12/main -o '-c listen_addresses=*' -w start"

echo "Setting up database and table..."

# Create user 'docker' if it doesn't exist.
psql --username=postgres <<-'EOF'
DO
$do$
BEGIN
   IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'docker') THEN
      CREATE ROLE docker LOGIN PASSWORD 'docker';
   END IF;
END
$do$;
EOF

# Create database 'docker' if it doesn't exist.
DB_EXISTS=$(psql --username=postgres -tAc "SELECT 1 FROM pg_database WHERE datname='knowledgemesh'")
if [ "$DB_EXISTS" != "1" ]; then
  psql --username=postgres -c "CREATE DATABASE knowledgemesh OWNER docker;"
fi

# Create the Records table in the 'knowledgemesh' database.
psql --username=docker --dbname=knowledgemesh <<-'EOF'
CREATE TABLE IF NOT EXISTS Records (
    id SERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    url TEXT NOT NULL,
    description TEXT,
    tags TEXT[],
    samaccountname TEXT,
    updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created TIMESTAMP DEFAULT CURRENT_TIMESTAMP, 
    reported TEXT[] DEFAULT ARRAY[]::TEXT[]
);
EOF

# Create the Records table in the 'knowledgemesh' database.
psql --username=docker --dbname=knowledgemesh <<-'EOF'
INSERT INTO public.records (title, url, description, tags, samaccountname)
VALUES
  ('KnowledgeMesh', 'https://github.com/jaengland/KnowledgeMesh', 'The sourcecode of KnowledgeMesh', '{code,KnowledgeMesh}', 'admin'),
  ('Example site', 'http://example.com/example.html', 'A description of the site', '{tag1,tag2}', 'user_id'),
  ('test site', 'http://test.com/test.html', 'A description of the site', '{tag1}', 'user_id'),
  ('Microsoft Home site', 'http://microsoft.com', 'This is microsoft''s really cool home site. it has lots of really cool software. I just can''t stop going on about how awesome it is. You really really really need to see it right now. Go go go go go go go go. Why are you still reading this!?', '{"cool site",software}', 'demo_user'),
  ('Google home site', 'http://google.com', 'The home site of Google', '{google}', 'demo_user'),
  ('Kubernetes documentation', 'https://kubernetes.io/docs/home/', 'The Kubernetes documentation site', '{kubernetes}', 'demo_user');
EOF

echo "Stopping temporary PostgreSQL server..."
su - postgres -c "/usr/lib/postgresql/12/bin/pg_ctl -D /var/lib/postgresql/12/main -m fast -w stop"

sysctl -w vm.max_map_count=262144

echo "Starting all services using supervisord..."
exec /usr/bin/supervisord -n
