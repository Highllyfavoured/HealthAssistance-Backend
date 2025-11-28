#!/usr/bin/env python3
import mysql.connector
from mysql.connector import Error
import os
from dotenv import load_dotenv

load_dotenv()

config = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', ''),
}

def execute_sql_file(connection, filename):
    cursor = connection.cursor()
    try:
        with open(filename, 'r') as sql_file:
            sql_script = sql_file.read()
            # Split script by semicolon and execute each statement
            statements = sql_script.split(';')
            for statement in statements:
                if statement.strip():
                    cursor.execute(statement)
        connection.commit()
        print(f"Successfully executed {filename}")
    except Error as err:
        print(f"Error: {err}")
        connection.rollback()
    finally:
        cursor.close()

def main():
    try:
        connection = mysql.connector.connect(**config)
        if connection.is_connected():
            db_info = connection.get_server_info()
            print(f"Successfully connected to MySQL Server version {db_info}")
            execute_sql_file(connection, 'scripts/init_database.sql')
    except Error as err:
        print(f"Error while connecting to MySQL: {err}")
    finally:
        if connection.is_connected():
            connection.close()
            print("MySQL connection is closed")

if __name__ == "__main__":
    main()
