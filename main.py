from database.db_manager import DBManager
from database.db_utils import create_database, create_tables, get_db_config
from api.hh_api import get_employer_data, get_vacancies
from api.config import COMPANIES
import psycopg2


def fill_database():
    """Заполняет БД данными с hh.ru"""
    conn = psycopg2.connect(**get_db_config())
    try:
        with conn.cursor() as cursor:
            cursor.execute("TRUNCATE TABLE vacancies RESTART IDENTITY CASCADE")
            cursor.execute("TRUNCATE TABLE employers RESTART IDENTITY CASCADE")

            for company_id in COMPANIES.values():
                employer = get_employer_data(company_id)
                cursor.execute(
                    "INSERT INTO employers VALUES (%s, %s, %s)",
                    (employer['id'], employer['name'], employer['alternate_url'])
                )

                vacancies = get_vacancies(company_id)
                for vacancy in vacancies:
                    salary = vacancy.get('salary') or {}
                    cursor.execute(
                        """INSERT INTO vacancies VALUES
                        (DEFAULT, %s, %s, %s, %s, %s)""",
                        (vacancy['employer']['id'],
                         vacancy['name'],
                         salary.get('from'),
                         salary.get('to'),
                         vacancy['alternate_url'])
                    )
        conn.commit()
    finally:
        conn.close()


def user_interface():
    """Полный интерфейс со всеми пунктами меню"""
    with DBManager() as db:
        while True:
            print("\n1. Список компаний и количество вакансий")
            print("2. Все вакансии")
            print("3. Средняя зарплата")
            print("4. Вакансии с зарплатой выше средней")
            print("5. Поиск вакансий по ключевому слову")
            print("0. Выход")

            choice = input("Выберите пункт: ").strip()

            if choice == "1":
                print("\nКомпании и количество вакансий:")
                for name, count in db.get_companies_and_vacancies_count():
                    print(f"{name}: {count}")

            elif choice == "2":
                print("\nВсе вакансии:")
                for company, title, salary_from, salary_to, url in db.get_all_vacancies():
                    print(f"{company}: {title} ({salary_from or '?'}-{salary_to or '?'}) | {url}")

            elif choice == "3":
                print(f"\nСредняя зарплата: {db.get_avg_salary():.2f} руб.")

            elif choice == "4":
                print("\nВакансии с зарплатой выше средней:")
                for company, title, salary, url in db.get_vacancies_with_higher_salary():
                    print(f"{company}: {title} (от {salary} руб.) | {url}")

            elif choice == "5":
                keyword = input("\nВведите ключевое слово: ").strip()
                print(f"Результаты поиска по '{keyword}':")
                for company, title, salary, url in db.get_vacancies_with_keyword(keyword):
                    print(f"{company}: {title} (от {salary or '?'} руб.) | {url}")

            elif choice == "0":
                print("\nРабота программы завершена")
                break


if __name__ == "__main__":
    create_database()
    create_tables()
    fill_database()
    user_interface()
