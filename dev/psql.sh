dev_dir="$(dirname -- "$(which -- "$0" 2>/dev/null || realpath -- "$0")")"
user=$(cat "$dev_dir/../dev-config.json" | jq -r '.pg.user')
password=$(cat "$dev_dir/../dev-config.json" | jq -r '.pg.password')
db=$(cat "$dev_dir/../dev-config.json" | jq -r '.pg.db')

PGPASSWORD=$password psql $db -h localhost -p 5432 -U $user 
