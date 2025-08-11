until nc -z $DB_HOST $DB_PORT; do
    echo "Waiting for PostgreSQL..."
    sleep 1
done

echo "PostgreSQL is ready"
