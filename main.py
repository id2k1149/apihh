"""
Поиск средней зарплаты и наиболее актуальных навыков для какой-либо вакансии
"""

import requests
import json
from collections import Counter


def vacancy_page(parameters):
    domain = 'https://api.hh.ru/'
    url_vacancies = f'{domain}vacancies'
    single_page = requests.get(url_vacancies, params=parameters).json()
    return single_page


params = {}
key_word = input('Наберите ключевое слово для поиска вакансии ')
params['text'] = key_word


region = input('Вакансия в Москве? y/n ')
if region == 'y':
    params['area'] = 1
else:
    params['area'] = 113
result = vacancy_page(params)

print('******************************')
total_found = result['found']
total_pages = result['pages']
vacancies_per_page = result['per_page']
print(f'найдено {total_found} вакансий')
print('******************************')
print('Идет просмотр страницы вакансий, подсчет средней зарплаты и анализ необходимых навыков....')
print('Пожалуйста, подождите. Это может занять некоторое время....')


count = 0
salary_count = 0
salary_average = 0
# количество страниц для расчетов можно сделать = total_pages
pages_to_analyse = 1
for j in range(pages_to_analyse):
    page = j
    params['page'] = page
    result = vacancy_page(params)
    items = result['items']
    skill_list = []
    vacancy_with_skill_count = 0
    for i in range(len(items)):
        count += 1
        item = items[i]
        url = item['url']
        # вывод на печать чтобы показать что процесс идет...
        print(f'#{count} - {url}')

        new_result = requests.get(url).json()
        skill = new_result['key_skills']
        if len(skill) != 0:
            vacancy_with_skill_count += 1
            for k in range(len(skill)):
                s1 = skill[k].get('name')
                skill_list.append(s1)

        if item['salary'] is not None:
            salary = item['salary']
            if salary['currency'] == 'RUR':
                if salary['from'] is not None:
                    salary_count += 1
                    salary_average += salary['from']

print('*' * 60)
print(f'Среди просмотренных вакансий было только {salary_count} с указанием зарплаты')
print(f'Средняя зарплата = {salary_average//salary_count} руб')
print('*' * 60)
print(f'Вакансий с требованиями было {vacancy_with_skill_count}')

print('Часто встречающиеся требования - ')
short_skill_list = [x for x in skill_list if skill_list.count(x) > 2]

skill_rating = Counter(short_skill_list).most_common()

skill_count = 0
for i in skill_rating:
    skill_count += i[1]

requirements = []
for i in skill_rating:
    share = float("{0:.1f}".format(i[1] * 100 / skill_count))
    print(f'{i[0]} встречается в {i[1]} вакансиях -> {share}%')
    element = {'name': i[0], 'count': i[1], 'persent': share}
    requirements.append(element)

print('*' * 60)
output_file = 'saved_data.json'
print(f'Все результаты будут сохранены в файл {output_file}')

data = []
e_keywords = {'keywords': key_word}
data.append(e_keywords)
e_count = {'count': vacancy_with_skill_count}
data.append(e_count)
e_requirements = {'requirements': requirements}
data.append(e_requirements)

data_json = json.dumps(data)

with open(output_file, 'w', encoding='utf-8') as json_file:
    json.dump(data_json, json_file)
