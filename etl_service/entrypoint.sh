# etl_service/entrypoint.sh
#!/bin/sh
while true; do
  pg_dump $SOURCE_DB_URL | psql $WAREHOUSE_DB_URL
  sleep 60
done
