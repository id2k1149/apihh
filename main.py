from flask import Flask, render_template, request
from hh_api import result_page

app = Flask(__name__)
current_year = '2020'


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
    return render_template('form.html',
                           year=current_year)


@app.route('/form/', methods=['POST'])
def form_post():
    key_word = request.form['vacancy_query']
    skills_for_bot, requirements = result_page(key_word)
    return render_template('results.html',
                           key_word=key_word,
                           skills=requirements,
                           year=current_year)


@app.route('/results/')
def results():
    # with open('file_Python.json', 'r', encoding='utf-8') as f:
    #     text = f.read()
    return render_template('results.html',
                           # text=text,
                           year=current_year)


if __name__ == "__main__":
    app.run(debug=True)
