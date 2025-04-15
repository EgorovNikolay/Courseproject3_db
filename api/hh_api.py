from typing import Dict, List

import requests


def get_employer_data(employer_id: str) -> Dict:
    """Получает данные компании с hh.ru"""
    response = requests.get(f"https://api.hh.ru/employers/{employer_id}")
    response.raise_for_status()
    return response.json()


def get_vacancies(employer_id: str) -> List[Dict]:
    """Получает вакансии компании с hh.ru"""
    params = {"employer_id": employer_id, "per_page": 100}
    response = requests.get("https://api.hh.ru/vacancies", params=params)
    response.raise_for_status()
    return response.json().get("items", [])
