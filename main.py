import requests
import json
from settings import TG_API_URL
import pprint
from collections import Counter


def vacancy_page(parameters):
    domain = TG_API_URL
    url_vacancies = f'{domain}vacancies'
    single_page = requests.get(url_vacancies, params=parameters).json()
    return single_page


def result_page(vacancy):
    parameters = {'text': vacancy, 'area': 1, 'page': 1}
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
    for i in skill_rating:
        share = float("{0:.1f}".format(i[1] * 100 / skill_count))
        element_for_bot = f"{i[0]} {share}%\n"
        bot_requirements += element_for_bot
        element = {'skill': i[0], '%%': share}
        requirements.append(element)

    if bot_requirements and bot_requirements.strip():
        top_skills = first_line + bot_requirements
        output_file = f"file_{vacancy}.json"
        data['vacancy'] = vacancy
        data['requirements'] = requirements
        with open(output_file, 'w', encoding='utf-8') as json_file:
            json.dump(data, json_file)
    else:
        top_skills = f"Sorry, didn't find any skills for {vacancy} vacancy :("
    return top_skills


def vacancy_salary(vacancy):
    parameters = {'text': vacancy, 'area': 1, 'page': 1}
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
    avg_salary = f'Средняя зарплата = {salary_average // salary_count} руб'
    return avg_salary


# key_word = input('Наберите ключевое слово для поиска вакансии ')
# skills = result_page(key_word)
# s = vacancy_salary(key_word)
# print(s)
# print(skills)

