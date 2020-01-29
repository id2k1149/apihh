from flask import Flask, render_template, request
from hh_api import result_page, vacancy_salary
import sqlite3

app = Flask(__name__)
current_year = '2020'

# Подключение к базе данных
conn = sqlite3.connect('hhdb.sqlite', check_same_thread=False)
# Создаем курсор
cursor = conn.cursor()


@app.route("/")
def index():
    return render_template('index.html',
                           year=current_year)


@app.route('/contacts/')
def contacts():
    neu_contacts = {
        'phone': '+7 (499) 648-67-44',
        'email': 'info@neural-university.ru'
    }
    # phone_number = '+7 (499) 648-67-44'
    # e_mail = 'info@neural-university.ru'
    return render_template('contacts.html',
                           # phone=phone_number,
                           # email=e_mail,
                           **neu_contacts,
                           year=current_year)


# @app.route('/form/', methods=['GET', 'POST'])
# def form():
#     if request.method == 'POST':
#         pass
#     else:
#         return render_template('form.html',
#                                year=current_year)


@app.route('/form/', methods=['GET'])
def form_get():
    cursor.execute('SELECT * from regions')
    region_list = cursor.fetchall()
    return render_template('form.html',
                           year=current_year,
                           region_list=region_list)


@app.route('/form/', methods=['POST'])
def form_post():
    key_word = request.form['vacancy_query']
    id_region = request.form['id_region']

    skills_for_bot, requirements = result_page(key_word, id_region)
    cursor.execute(
        'SELECT name from regions where hh_region_id=?',
        (id_region,))
    city = cursor.fetchall()[0][0]
    salary = vacancy_salary(key_word, id_region)

    if len(requirements) != 0:
        cursor.execute('SELECT * from vacancy where name=? and region_id=?',
                       (key_word, id_region))
        result = cursor.fetchall()
        if len(result) == 0:
            cursor.execute(
                "insert into vacancy(name, region_id) VALUES (?,?)",
                (key_word, id_region))
            conn.commit()
            cursor.execute(
                'SELECT id from vacancy where name=? and region_id=?',
                (key_word, id_region))
            vr_id = cursor.fetchall()[0][0]
            for each_item in requirements:
                item_list = list(each_item.values())
                skill = item_list[1]
                cursor.execute(
                    'SELECT id from skills where name=?',
                    (skill,))
                skill_id = cursor.fetchall()
                if len(skill_id) == 0:
                    cursor.execute(
                        "insert into skills(name) VALUES (?)",
                        (skill,))
                    conn.commit()
                    cursor.execute(
                        'SELECT id from skills where name=?',
                        (skill,))
                    skill_id = cursor.fetchall()
                sk_id = skill_id[0][0]
                cursor.execute(
                    "insert into vacancy_skills(vacancy_id, skill_id) VALUES "
                    "(?,?)",
                    (vr_id, sk_id))
                conn.commit()

    return render_template('results.html',
                           key_word=key_word,
                           query_region=city,
                           skills=requirements,
                           salary=salary,
                           year=current_year)


@app.route('/results/')
def results():

    return render_template('results.html',
                           year=current_year)


@app.route('/skills_hdbk/', methods=['GET'])
def skills_get():
    query = "select v.id, v.name, r.name from vacancy v, regions r " \
            "where  v.region_id == r.id "

    cursor.execute(query)
    vacancy_region_list = cursor.fetchall()

    return render_template('skills_hdbk.html',
                           vacancy_region_list=vacancy_region_list,
                           year=current_year)


@app.route('/skills_hdbk/', methods=['POST'])
def skills_post():
    vac_id = request.form['vacancy_id']

    cursor.execute("select s.name from vacancy_skills vs, skills s where "
                   "vs.skill_id=s.id and vacancy_id=?", (vac_id,))

    skills_list = cursor.fetchall()

    cursor.execute("select v.name from vacancy v where v.id=?", (vac_id,))
    vacancy = cursor.fetchall()[0][0]

    cursor.execute("select r.name from vacancy v, regions r where "
                   "v.region_id = r.id and v.id=?", (vac_id,))
    city = cursor.fetchall()[0][0]

    return render_template('skills_result.html',
                           result_list=skills_list,
                           vacancy=vacancy,
                           city=city,
                           year=current_year)


@app.route('/skills_result/')
def skills_result():

    return render_template('skills_result.html',
                           year=current_year)


if __name__ == "__main__":
    app.run(debug=True)
