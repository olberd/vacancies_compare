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


if __name__ == '__main__':
    pprint(get_vacancies_by_lang())
