dev_dir="$(dirname -- "$(which -- "$0" 2>/dev/null || realpath -- "$0")")"
user=postgres
db=postgres
password=$(cat "$dev_dir/../dev-config.json" | jq -r '.pg.admin_password')

PGPASSWORD=$password psql $db -h localhost -p 5432 -U $user 
