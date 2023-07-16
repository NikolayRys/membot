dev_dir="$(dirname -- "$(which -- "$0" 2>/dev/null || realpath -- "$0")")"
admin_password=$(cat "$dev_dir/../dev-config.json" | jq -r '.pg.admin_password')
user=$(cat "$dev_dir/../dev-config.json" | jq -r '.pg.user')
password=$(cat "$dev_dir/../dev-config.json" | jq -r '.pg.password')
db=$(cat "$dev_dir/../dev-config.json" | jq -r '.pg.db')

docker run -e POSTGRES_PASSWORD=$admin_password -d --name pg-vector -p 127.0.0.1:5432:5432 ankane/pgvector

sleep 2;

PGPASSWORD=$admin_password psql -h localhost -p 5432 -U postgres -c "CREATE USER $user WITH PASSWORD '$password';"; 
PGPASSWORD=$admin_password psql -h localhost -p 5432 -U postgres -c "CREATE DATABASE $db;"; 
PGPASSWORD=$admin_password psql -h localhost -p 5432 -U postgres -c "GRANT ALL PRIVILEGES ON DATABASE $db TO $user;"; 
PGPASSWORD=$admin_password psql -h localhost -p 5432 -U postgres -c "ALTER DATABASE $db OWNER TO $user;"; 
PGPASSWORD=$admin_password psql -h localhost -p 5432 -U postgres -c "ALTER USER $user SET search_path TO public;"; 
PGPASSWORD=$admin_password psql -h localhost -p 5432 -U postgres -c "CREATE EXTENSION IF NOT EXISTS vector;" $db; 
