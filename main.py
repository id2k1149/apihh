from flask import Flask, render_template, request
from hh_api import result_page, vacancy_salary
from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import create_engine
from sqlalchemy import ForeignKey
from sqlalchemy import Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

engine = create_engine('sqlite:///orm.sqlite',
                       connect_args={'check_same_thread': False},
                       echo=True)

Base = declarative_base()


class Regions(Base):
    __tablename__ = 'regions'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    hh_region_id = Column(Integer)

    def __init__(self, name, hh_region_id):
        self.name = name
        self.hh_region_id = hh_region_id

    def __str__(self):
        return f'{self.id}, {self.name}: {self.hh_region_id}'


class Skills(Base):
    __tablename__ = 'skills'
    id = Column(Integer, primary_key=True)
    name = Column(String)

    def __init__(self, name):
        self.name = name

    def __str__(self):
        return f'{self.id}, {self.name}'


class Vacancy(Base):
    __tablename__ = 'vacancy'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    region_id = Column(Integer, ForeignKey('regions.id'))

    def __init__(self, name, region_id):
        self.name = name
        self.region_id = region_id


vacancy_skills = Table('vacancy_skills', Base.metadata,
                       Column('id', Integer, primary_key=True),
                       Column('vacancy_id', Integer, ForeignKey('vacancy.id')),
                       Column('skill_id', Integer, ForeignKey('skills.id'))
                       )

Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()

region_start_list = ('Москва',
                     'Санкт-Петербург',
                     'Екатеринбург',
                     'Новосибирск')
i = 1
for each in region_start_list:
    region_name_check = session.query(Regions).filter(
        Regions.name == each).all()

    if len(region_name_check) == 0:
        region = Regions(each, i)
        i += 1
        session.add(region)
    else:
        continue

session.commit()

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
    return render_template('contacts.html',
                           **neu_contacts,
                           year=current_year)


@app.route('/form/', methods=['GET'])
def form_get():
    region_query = session.query(Regions).all()

    region_list = []
    for each in region_query:
        each_list = [each.id, each.name, each.hh_region_id]
        region_list.append(each_list)

    return render_template('form.html',
                           year=current_year,
                           region_list=region_list)


@app.route('/form/', methods=['POST'])
def form_post():
    key_word = request.form['vacancy_query']

    id_region = int(request.form['id_region'])

    skills_for_bot, requirements = result_page(key_word, id_region)

    region_query = session.query(Regions.name).filter(Regions.hh_region_id == id_region).all()

    city = region_query[0][0]

    salary = vacancy_salary(key_word, id_region)

    if len(requirements) != 0:

        check = session.query(Vacancy).\
            filter(Vacancy.region_id == id_region).\
            filter(Vacancy.name == key_word).all()

        if len(check) == 0:
            vacancy = Vacancy(key_word, id_region)
            session.add(vacancy)
            session.commit()

            for each_item in requirements:
                item_list = list(each_item.values())
                skill = item_list[1]

                new_query = session.query(Skills.id).filter(
                    Skills.name == skill).all()
                skill_id = new_query

                if len(skill_id) == 0:
                    new_skill = Skills(skill)
                    session.add(new_skill)
                    session.commit()

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


if __name__ == "__main__":
    app.run(debug=True)
