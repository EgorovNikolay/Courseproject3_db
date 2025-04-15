import os
from typing import Any, Dict

import psycopg2
from dotenv import load_dotenv

load_dotenv()


def get_db_config() -> Dict[str, Any]:
    """Получает конфиг подключения из переменных окружения"""
    return {
        "host": os.getenv("DB_HOST"),
        "database": os.getenv("DB_NAME"),
        "user": os.getenv("DB_USER"),
        "password": os.getenv("DB_PASSWORD"),
        "port": os.getenv("DB_PORT", "5432"),
    }


def create_database():
    """Создает новую БД PostgreSQL"""
    config = get_db_config()
    conn = psycopg2.connect(
        host=config["host"],
        user=config["user"],
        password=config["password"],
        port=config["port"],
    )
    conn.autocommit = True
    try:
        with conn.cursor() as cursor:
            cursor.execute(f"CREATE DATABASE {config['database']}")
    except psycopg2.errors.DuplicateDatabase:
        pass
    finally:
        conn.close()


def create_tables():
    """Создает таблицы employers и vacancies"""
    conn = psycopg2.connect(**get_db_config())
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS employers (
                    employer_id VARCHAR(20) PRIMARY KEY,
                    name VARCHAR(100) NOT NULL,
                    url VARCHAR(100)
                )
            """
            )
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS vacancies (
                    vacancy_id SERIAL PRIMARY KEY,
                    employer_id VARCHAR(20) REFERENCES employers(employer_id),
                    title VARCHAR(100) NOT NULL,
                    salary_from INTEGER,
                    salary_to INTEGER,
                    url VARCHAR(100)
                )
            """
            )
        conn.commit()
    finally:
        conn.close()
