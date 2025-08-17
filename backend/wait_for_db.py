import os
import socket
import time


def wait_for_db():
    db_host = os.getenv("DB_HOST")
    db_port = int(os.getenv("DB_PORT", 5432))

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    while True:
        try:
            s.connect((db_host, db_port))
            s.close()
            print(f"PostgreSQL at {db_host}:{db_port} is ready")
            return
        except socket.error:
            print(f"Waiting for PostgreSQL at {db_host}:{db_port}...")
            time.sleep(1)


if __name__ == "__main__":
    wait_for_db()
