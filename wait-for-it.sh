#!/bin/bash
# wait-for-it.sh

# DB'ye bağlanana kadar bekleyin
until pg_isready -h "$DB_HOST" -U "$DB_USER"; do
  echo "Waiting for PostgreSQL to be ready..."
  sleep 2
done

# Eğer her şey yolunda ise Django'nun çalıştırılmasını başlatın
exec "$@"
