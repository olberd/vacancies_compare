import json
from pprint import pprint

import requests


hh_url = 'https://api.hh.ru/vacancies/'
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; rv:91.0) Gecko/20100101 Firefox/91.0'
}


def get_vacancies_by_lang():
    programming_languages = ['Python', 'Java', 'JavaScript', 'C', 'C#', 'Go', 'Swift',
                             'PHP', 'Ruby', 'C++', 'Objective-C', 'Scala', ]

    vacancies_by_languages = {}
    for lang in programming_languages:
        payload = {
            'text': f'Программист { lang }',
            'area': 1,
            'period': 30,
        }

        response = requests.get(hh_url, params=payload)
        response.raise_for_status()
        vacancies = json.loads(response.text)
        vacancies_by_languages[lang] = vacancies['found']

    return vacancies_by_languages


def get_job_salary():
    payload = {
        'text': 'Программист Python',
        'area': 1,
        'period': 30,
    }
    response = requests.get(hh_url, params=payload)
    response.raise_for_status()
    vacancies = json.loads(response.text)
    for job in vacancies['items']:
        predict_rub_salary(job['salary'])


def predict_rub_salary(vacancy):
    if vacancy and vacancy['currency'] == 'RUR':
        if vacancy['from'] and vacancy['to']:
            print((vacancy['from'] + vacancy['to']) / 2)
        elif vacancy['from'] and not vacancy['to']:
            print(vacancy['from'] * 1.2)
        elif not vacancy['from'] and vacancy['to']:
            print(vacancy['to'] * 0.8)
    else:
        print(None)


if __name__ == '__main__':
    # pprint(get_vacancies_by_lang())
    get_job_salary()
