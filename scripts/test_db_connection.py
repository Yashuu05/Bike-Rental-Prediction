import os
import sys
from urllib.parse import quote_plus
from dotenv import load_dotenv
import pymysql

# Load credentials from .env
load_dotenv()

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", "3306"))
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_NAME = os.getenv("DB_NAME", "bikerental_db")

print("=" * 60)
print("AWS RDS MySQL Connection Diagnostic Tool")
print("=" * 60)
print(f"Host:     {DB_HOST}")
print(f"Port:     {DB_PORT}")
print(f"User:     {DB_USER}")
print(f"Database: {DB_NAME}")
print("Connecting (timeout: 5s)...")

try:
    connection = pymysql.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        port=DB_PORT,
        connect_timeout=5,
        charset='utf8mb4'
    )
    print("\n[SUCCESS] Successfully established TCP connection and authenticated with AWS RDS MySQL!")
    
    with connection.cursor() as cursor:
        cursor.execute("SELECT VERSION();")
        version = cursor.fetchone()
        print(f"MySQL Version: {version[0]}")
        
        cursor.execute("SHOW DATABASES;")
        databases = [row[0] for row in cursor.fetchall()]
        print(f"Available Databases: {databases}")
        
        if DB_NAME in databases:
            print(f"[OK] Database '{DB_NAME}' exists.")
        else:
            print(f"[NOTE] Database '{DB_NAME}' does not exist yet. Creating it now...")
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{DB_NAME}`;")
            print(f"[OK] Database '{DB_NAME}' created successfully.")

    connection.close()
    print("\n[READY] Database connection is verified and ready for the FastAPI web app!")
except pymysql.err.OperationalError as e:
    code, msg = e.args
    print(f"\n[FAILED] OperationalError ({code}): {msg}")
    if code == 2003:
        print("\n--> DIAGNOSIS: Connection Timed Out or Blocked.")
        print("    AWS RDS VPC Security Group is blocking incoming traffic on Port 3306.")
        print("    Please whitelist your current public IP in the AWS RDS Security Group inbound rules.")
    elif code == 1045:
        print("\n--> DIAGNOSIS: Access Denied (Invalid Username or Password).")
        print("    Please check DB_USER and DB_PASSWORD in your .env file.")
except Exception as ex:
    print(f"\n[ERROR] Unexpected error: {ex}")
