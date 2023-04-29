if [ -z "$1" ]; then
  echo "Error: Missing name"
  exit 1
fi
name="$1"

redis-cli FT.DROPINDEX $name
redis-cli \
    FT.CREATE $name \
    SCHEMA vector_field VECTOR \
    HNSW \
    6 \
        TYPE FLOAT64 \
        DIM 1536 \
        DISTANCE_METRIC COSINE
