from typing import List, Optional, Tuple

import psycopg2

from database.db_utils import get_db_config


class DBManager:
    """Класс для работы с данными вакансий в PostgreSQL"""

    def __init__(self):
        """Устанавливает соединение с БД"""
        self.conn = psycopg2.connect(**get_db_config())

    def get_companies_and_vacancies_count(self) -> List[Tuple[str, int]]:
        """Возвращает список компаний с количеством вакансий"""
        with self.conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT e.name, COUNT(v.vacancy_id)
                FROM employers e
                LEFT JOIN vacancies v ON e.employer_id = v.employer_id
                GROUP BY e.name
            """
            )
            return cursor.fetchall()

    def get_all_vacancies(
        self,
    ) -> List[Tuple[str, str, Optional[int], Optional[int], str]]:
        """Возвращает все вакансии с деталями"""
        with self.conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT e.name, v.title, v.salary_from, v.salary_to, v.url
                FROM vacancies v
                JOIN employers e ON v.employer_id = e.employer_id
            """
            )
            return cursor.fetchall()

    def get_avg_salary(self) -> float:
        """Вычисляет среднюю зарплату по вакансиям"""
        with self.conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT AVG(salary_from)
                FROM vacancies
                WHERE salary_from IS NOT NULL
            """
            )
            return round(float(cursor.fetchone()[0] or 0), 2)

    def get_vacancies_with_higher_salary(self) -> List[Tuple[str, str, int, str]]:
        """Возвращает вакансии с зарплатой выше средней"""
        avg = self.get_avg_salary()
        with self.conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT e.name, v.title, v.salary_from, v.url
                FROM vacancies v
                JOIN employers e ON v.employer_id = e.employer_id
                WHERE v.salary_from > %s
            """,
                (avg,),
            )
            return cursor.fetchall()

    def get_vacancies_with_keyword(
        self, keyword: str
    ) -> List[Tuple[str, str, Optional[int], str]]:
        """Ищет вакансии по ключевому слову в названии"""
        with self.conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT e.name, v.title, v.salary_from, v.url
                FROM vacancies v
                JOIN employers e ON v.employer_id = e.employer_id
                WHERE LOWER(v.title) LIKE %s
            """,
                (f"%{keyword.lower()}%",),
            )
            return cursor.fetchall()

    def close(self):
        """Закрывает соединение с БД"""
        self.conn.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
