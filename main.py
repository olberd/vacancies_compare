import os
from itertools import count
from dotenv import load_dotenv
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


def get_vacancies_by_language_hh(lang, page):
    moscow_id = 1
    month = 30
    hh_url = 'https://api.hh.ru/vacancies/'
    payload = {
        'text': f'Программист {lang}',
        'area': moscow_id,
        'period': month,
        'page': page,
    }
    headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                             'Chrome/106.0.0.0 Safari/537.36'}
    response = requests.get(hh_url, headers=headers, params=payload)
    response.raise_for_status()
    return response.json()


def parse_language_vacancies__hh(languages):
    page_payload = []
    salaries = []
    vacancies_by_languages = {}
    for lang in languages:
        vacancies_by_languages[lang] = {}
        for page in count(0):
            page_payload = get_vacancies_by_language_hh(lang, page)
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


def get_vacancies_by_language_superjob(language, superjob_token, page=0):
    vacancies_url = 'https://api.superjob.ru/2.20/vacancies/'
    moscow_id = 4
    job_catalogues = 48
    headers = {
        'X-Api-App-Id': superjob_token,
    }
    params = {
        'town': moscow_id,
        'catalogues': job_catalogues,
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
    if not salary_currency and salary_currency != 'rub':
        return
    payment_from = vacancy.get('payment_from', None)
    payment_to = vacancy.get('payment_to', None)
    return predict_salary(payment_from, payment_to)


def parse_language_vacancies_superjob(languages, superjob_token):
    vacancies_by_languages = {}
    for language in languages:
        salaries = []
        more = True
        page = 0
        while more:
            response = get_vacancies_by_language_superjob(language, superjob_token, page)

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


def get_table_rows(lang_statistic):
    rows = [['Язык программирования', 'Вакансий найдено', 'Вакансий обработано', 'Средняя зарплата']]
    for lang, statistic in lang_statistic.items():
        rows.append([lang, statistic['vacancies_found'], statistic['vacancies_processed'], statistic['average_salary']])
    return rows


def create_table_hh():
    hh_title = 'Средние зарплаты на Head Hunter'
    statistic_by_lang_hh = parse_language_vacancies__hh(LANGUAGES)
    rows = get_table_rows(statistic_by_lang_hh)
    table_instance = AsciiTable(rows, hh_title)
    return table_instance.table


def create_table_sj(superjob_token):
    sj_title = 'Средние зарплаты на SuperJob'
    statistic_by_lang_sj = parse_language_vacancies_superjob(LANGUAGES, superjob_token)
    rows = get_table_rows(statistic_by_lang_sj)
    table_instance = AsciiTable(rows, sj_title)
    return table_instance.table


if __name__ == '__main__':
    load_dotenv()
    superjob_token = os.environ.get('SUPERJOB_TOKEN')
    print(create_table_hh())
    print(create_table_sj(superjob_token))
