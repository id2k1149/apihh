import requests
import json
from settings import TG_API_URL
import pprint
from collections import Counter
import sqlite3

# Подключение к базе данных
conn = sqlite3.connect('hhdb.sqlite', check_same_thread=False)
# Создаем курсор
cursor = conn.cursor()


def vacancy_page(parameters):
    domain = 'https://api.hh.ru/'
    url_vacancies = f'{domain}vacancies'
    single_page = requests.get(url_vacancies, params=parameters).json()
    return single_page


def result_page(vacancy, id_region):
    parameters = {'text': vacancy,
                  'area': id_region,
                  'page': 1}
    count = 0
    skill_list = []
    data = {}
    result = vacancy_page(parameters)
    items = result['items']
    vacancy_with_skill_count = 0
    for i in range(len(items)):
        count += 1
        item = items[i]
        url = item['url']

        new_result = requests.get(url).json()
        skill = new_result['key_skills']
        if len(skill) != 0:
            vacancy_with_skill_count += 1
            for k in range(len(skill)):
                s1 = skill[k].get('name')
                skill_list.append(s1)

    short_skill_list = [x for x in skill_list if skill_list.count(x) > 1]

    skill_rating = Counter(short_skill_list).most_common()

    skill_count = 0
    for i in skill_rating:
        skill_count += i[1]

    first_line = f"Top skills(%%) for {vacancy} vacancy:\n"
    bot_requirements = ""
    requirements = []
    number = 1
    for i in skill_rating:
        share = float("{0:.1f}".format(i[1] * 100 / skill_count))
        element_for_bot = f"{i[0]} {share}%\n"
        bot_requirements += element_for_bot
        element = {'nn': number, 'skill': i[0], 'percents': share}
        requirements.append(element)
        number += 1

    if bot_requirements and bot_requirements.strip():
        skills_for_bot = first_line + bot_requirements
        data['vacancy'] = vacancy
        data['requirements'] = requirements

    else:
        skills_for_bot = f"Sorry, didn't find any skills for {vacancy} vacancy :("
    return skills_for_bot, requirements


def vacancy_salary(vacancy, id_region):
    parameters = {'text': vacancy, 'area': id_region, 'page': 1}
    count = 0
    salary_count = 0
    salary_average = 0
    result = vacancy_page(parameters)
    items = result['items']

    for i in range(len(items)):
        count += 1
        item = items[i]

        if item['salary'] is not None:
            salary = item['salary']
            if salary['currency'] == 'RUR':
                if salary['from'] is not None:
                    salary_count += 1
                    salary_average += salary['from']

    if salary_count == 0:
        avg_salary = f'данных по зарплате нет'
    else:
        avg_salary = f'средняя зарплата {salary_average // salary_count} руб'
    return avg_salary


# key_word = input('Наберите ключевое слово для поиска вакансии ')
# print(key_word)
# skills, req = result_page(key_word, 1)
# # s = vacancy_salary(key_word)
# # print(s)
# # print(type(req))
#
# for element in req:
#     # print(type(element))
#     # for key, value in element.items():
#     #     print(value)
#     print(element['nn'], element['skill'], element['percents'])

