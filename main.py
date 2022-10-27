import json
import os
from itertools import count
from dotenv import load_dotenv
from pprint import pprint
import requests
from terminaltables import AsciiTable

LANGUAGES = ['Swift', 'Python', 'Java', 'JavaScript', 'C', 'C#', 'Go',
             'PHP', 'Ruby', 'C++', 'Objective-C', 'Scala', '1С']


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
        vacancies_by_languages[lang] = {}
        vacancies_by_languages[lang] = {
            'vacancies_found': page_payload['found'],
            'vacancies_processed': len(salaries),
            'average_salary': int(avg_language_salary),
        }
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
        vacancies_by_languages[language] = {
            'vacancies_found': response['total'],
            'vacancies_processed': processed_vacancies,
            'average_salary': int(avg_language_salary),
        }
    return vacancies_by_languages


def hh_table():
    hh_title = 'Средние зарплаты на Head Hunter'
    sj_title = 'Средние зарплаты на SuperJob'
    vacancies_by_lang_hh = get_vacancies_by_lang_hh(LANGUAGES)
    rows = [['Язык программирования', 'Вакансий найдено', 'Вакансий обработано', 'Средняя зарплата']]

    for lang, statistic in vacancies_by_lang_hh.items():
        rows.append([lang, statistic['vacancies_found'], statistic['vacancies_processed'], statistic['average_salary']])

    table_instance = AsciiTable(rows, hh_title)
    print(table_instance.table)


def sj_table(superjob_token):
    rows = [['Язык программирования', 'Вакансий найдено', 'Вакансий обработано', 'Средняя зарплата']]
    sj_title = 'Средние зарплаты на SuperJob'
    vacancies_by_lang_sj = parse_language_vacancies_superjob(LANGUAGES, superjob_token)
    for lang, statistic in vacancies_by_lang_sj.items():
        rows.append([lang, statistic['vacancies_found'], statistic['vacancies_processed'], statistic['average_salary']])
    table_instance = AsciiTable(rows, sj_title)
    print(table_instance.table)


if __name__ == '__main__':
    hh_table()
    load_dotenv()
    superjob_token = os.environ.get('SUPERJOB_TOKEN')
    sj_table(superjob_token)
