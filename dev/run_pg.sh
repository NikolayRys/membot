dev_dir="$(dirname -- "$(which -- "$0" 2>/dev/null || realpath -- "$0")")"
pg_password=$(cat "$dev_dir/../dev-config.json" | jq -r '.pg.password')

docker run -e POSTGRES_PASSWORD=$pg_password -d --name pg-vector -p 127.0.0.1:5432:5432 ankane/pgvector
