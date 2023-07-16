dev_dir="$(dirname -- "$(which -- "$0" 2>/dev/null || realpath -- "$0")")"
pg_password=$(cat "$dev_dir/../dev-config.json" | jq -r '.pg.password')

PGPASSWORD=$pg_password psql -h localhost -p 5432 -U postgres 
