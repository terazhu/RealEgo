import pymysql
import os

MYSQL_HOST = "mysql3cadafbd4a23.rds.ivolces.com"
MYSQL_PORT = 3306
MYSQL_USER = "tera"
MYSQL_PASSWORD = os.getenv("TERA_MYSQL_PASS", "tera")

try:
    conn = pymysql.connect(
        host=MYSQL_HOST,
        port=MYSQL_PORT,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD
    )
    cursor = conn.cursor()
    cursor.execute("CREATE DATABASE IF NOT EXISTS realego CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
    print("Database 'realego' checked/created.")
    conn.close()
except Exception as e:
    print(f"Error creating database: {e}")
