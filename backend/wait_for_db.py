import os
import time
import psycopg2
from psycopg2 import OperationalError


def wait_for_db():
    dbname = os.getenv('POSTGRES_DB')
    user = os.getenv('POSTGRES_USER')
    password = os.getenv('POSTGRES_PASSWORD')
    host = 'db'  # Имя сервиса в docker-compose

    max_retries = 15
    retry_delay = 5

    for i in range(max_retries):
        try:
            conn = psycopg2.connect(
                dbname=dbname,
                user=user,
                password=password,
                host=host
            )
            conn.close()
            print("PostgreSQL is ready!")
            return
        except OperationalError:
            print(f"Waiting for PostgreSQL... (attempt {i+1}/{max_retries})")
            time.sleep(retry_delay)
    
    print("Failed to connect to PostgreSQL after multiple attempts")
    exit(1)


if __name__ == '__main__':
    wait_for_db()
