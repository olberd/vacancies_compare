import json
from pprint import pprint

import requests

hh_url = 'https://api.hh.ru/vacancies/'
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; rv:91.0) Gecko/20100101 Firefox/91.0'
}


def get_vacancies_by_lang():
    programming_languages = ['Python', 'Java', 'JavaScript', 'C', 'C#', 'Go', 'Swift',
                             'PHP', 'Ruby', 'C++', 'Objective-C', 'Scala', 'Fortran']
    vacancies_by_languages = {}
    for lang in programming_languages:
        payload = {
            'text': f'Программист {lang}',
            'area': 1,
            'period': 30,
        }
        response = requests.get(hh_url, params=payload)
        response.raise_for_status()
        vacancies = json.loads(response.text)
        vacancies_processed, average_salary = get_average_salary(vacancies)
        vacancies_by_languages[lang] = {"vacancies_found": vacancies['found'],
                                        "vacancies_processed": vacancies_processed,
                                        "average_salary": average_salary,
                                        }
    return vacancies_by_languages


def predict_rub_salary(vacancy):
    salary = vacancy['salary']
    if salary and salary['currency'] == 'RUR':
        if salary['from'] and salary['to']:
            return (salary['from'] + salary['to']) / 2
        elif salary['from'] and not salary['to']:
            return salary['from'] * 1.2
        elif not salary['from'] and salary['to']:
            return salary['to'] * 0.8
    else:
        return None


def get_average_salary(vacancies):
    salaries = []
    salary_sum = 0
    for vacancy in vacancies['items']:
        salary = predict_rub_salary(vacancy)
        if salary:
            salaries.append(predict_rub_salary(vacancy))
            salary_sum = salary_sum + salary
    return len(salaries), int(salary_sum/len(salaries))


if __name__ == '__main__':
    pprint(get_vacancies_by_lang(), sort_dicts=False)
