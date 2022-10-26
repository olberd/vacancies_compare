import json
import os
from itertools import count
from dotenv import load_dotenv
from pprint import pprint
import requests
from terminaltables import AsciiTable

LANGUAGES = ['Swift', 'Python', 'Java', 'JavaScript', 'C', 'C#', 'Go',
             'PHP', 'Ruby', 'C++', 'Objective-C', 'Scala', 'Fortran']


def predict_salary(salary_from, salary_to):
    if salary_from and salary_to:
        return (salary_from + salary_to) / 2
    elif salary_from:
        return salary_from * 1.2
    elif salary_to:
        return salary_to * 0.8
    else:
        return None


def get_vacancies_by_lang_hh(languages):
    salaries = []
    vacancies_by_languages = {}
    for lang in languages:
        vacancies_by_languages[lang] = {}

        for page in count(0):
            hh_url = 'https://api.hh.ru/vacancies/'
            payload = {
                'text': f'Программист {lang}',
                'area': 1,
                'period': 30,
                'page': page,
            }
            response = requests.get(hh_url, params=payload)
            response.raise_for_status()
            page_payload = response.json()
            if page == page_payload['pages'] - 1:
                break

            for vacancy in page_payload['items']:
                if not vacancy['salary'] or vacancy['salary']['currency'] != 'RUR':
                    continue
                salary_from = vacancy['salary'].get('from')
                salary_to = vacancy['salary'].get('to')
                salaries.append(predict_salary(salary_from, salary_to))

        avg_language_salary = (sum(salaries) / len(salaries))
        vacancies_by_languages[lang]['vacancies_found'] = page_payload['found']
        vacancies_by_languages[lang]['vacancies_processed'] = len(salaries)
        vacancies_by_languages[lang]['average_salary'] = int(avg_language_salary)
    return vacancies_by_languages


def get_superjob_vacancies_by_language(language, superjob_token, page=0):
    vacancies_url = 'https://api.superjob.ru/2.20/vacancies/'
    headers = {
        'X-Api-App-Id': superjob_token,
    }
    params = {
        'town': 4,
        'catalogues': 48,
        'keyword': language,
        'page': page
    }
    response = requests.get(
        url=vacancies_url,
        headers=headers,
        params=params,
    )
    response.raise_for_status()
    return response.json()


def predict_rub_salary_for_sj(vacancy):
    salary_currency = vacancy.get('currency', None)
    if salary_currency and salary_currency == 'rub':
        payment_from = vacancy.get('payment_from', None)
        payment_to = vacancy.get('payment_to', None)
        return predict_salary(payment_from, payment_to)
    else:
        return None


def parse_language_vacancies_superjob(languages, superjob_token):
    vacancies_by_languages = {}
    for language in languages:
        salaries = []
        more = True
        page = 0
        while more:
            response = get_superjob_vacancies_by_language(language, superjob_token, page)

            more = response['more']
            for vacancy in response['objects']:
                vacancy_salary = predict_rub_salary_for_sj(vacancy)
                if vacancy_salary:
                    salaries.append(vacancy_salary)
            page += 1

        salaries_amount = sum(salaries)
        processed_vacancies = len(salaries)
        avg_language_salary = 0
        if processed_vacancies:
            avg_language_salary = (salaries_amount / processed_vacancies)
        vacancies_by_languages[language] = {}
        vacancies_by_languages[language]['vacancies_found'] = response['total']
        vacancies_by_languages[language]['vacancies_processed'] = processed_vacancies
        vacancies_by_languages[language]['average_salary'] = int(avg_language_salary)
    return vacancies_by_languages


if __name__ == '__main__':
    # print(get_vacancies_by_lang_hh(LANGUAGES[0:3]))
    load_dotenv()
    superjob_token = os.environ.get('SUPERJOB_TOKEN')

