from flask import (Flask, render_template, redirect, url_for, 
                   request, session, g, jsonify)
import requests
import os
import re

import hmac
import hashlib
import time

from models import db, User, Question, Quiz, db_add_new_data
from random import shuffle

# не работает
# BASE_DIR = os.getcwd()
BASE_DIR = os.path.dirname(__file__)
DB_PATH = os.path.join(BASE_DIR, 'db', 'db_quiz.db')

WEATHER_API_KEY = 'f23199e2033f9af89297e10d7cec508d'

html_config = {
    'admin':True,
    'debug':False
}

app = Flask(__name__,
            static_folder=os.path.join(BASE_DIR, 'static'),
            template_folder=os.path.join(BASE_DIR, 'templates'))

app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_PATH}'
app.config['SECRET_KEY'] = 'some secret key 12345'
db.init_app(app)

with app.app_context():
    db_add_new_data()
    quizes = Quiz.query.all()
    # for q in quizes:
        # print(q, q.name, q.user, q.question)
        # for quest in q.question:
        #     print(quest)
    print(quizes[1].question[1], quizes[1].question[1].answer)

    question = db.session.query(Question).get(1)

# QUIZ
@app.route('/quiz/', methods = ['POST', 'GET'])
def view_quiz():
    if request.method == 'GET':
        session['quiz_id'] = -1
        quizes = Quiz.query.all()
        # print(quizes)
        return render_template('start.html', 
                           quizes=quizes, 
                           html_config=html_config)
    session['quiz_id'] = request.form.get('quiz')
    session['question_n'] = 0
    session['question_id'] = 0
    session['right_answers'] = 0
    return redirect(url_for('view_question'))

# View Question
@app.route('/question/', methods = ['POST', 'GET'])
def view_question():
    # если квиз не выбран - отправляем на выбор
    if not session['quiz_id'] or session['quiz_id'] == -1:
        return redirect(url_for('view_quiz'))
    
    # if POST - значит ответ на вопрос
    if request.method == 'POST':
        question = Question.query.filter_by(id=session['question_id']).one()
        # если ответы сходятся - значит счетчик +1
        if question.answer == request.form.get('ans_text'):
            session['right_answers'] += 1
        # следующий вопрос
        session['question_n'] += 1

    quiz = Quiz.query.filter_by(id = session['quiz_id']).all()
    if int(session['question_n']) >= len(quiz[0].question):
        session['quiz_id'] = -1 # чтобы страница question больше не работала
        return redirect(url_for('view_result'))
    
    else:
        question = quiz[0].question[session['question_n']]
        session['question_id'] = question.id
        answers = [question.answer, question.wrong1, question.wrong2, question.wrong3]
        shuffle(answers)

        return render_template('question.html',
                               answers=answers,
                               question=question,
                               html_config=html_config)

# Просмотр всех вопросов    
@app.route('/questions/')
def view_questions():
    questions = Question.query.all()
    print(questions)
    return render_template('questions.html', 
                           questions = questions,
                           html_config = html_config)

# Страница с результатами квиза
@app.route('/result/')
def view_result():
    return render_template('result.html',
                           right=session['right_answers'],
                           total = session['question_n'],
                           html_config=html_config)

# страница просмотра Квизов
@app.route('/quizes_view/', methods = ['POST', 'GET'])
def view_quiz_edit():
    if request.method == 'POST':
        quiz = request.form.get('quiz')
        if quiz and len(quiz) > 3:
            user = User.query.all()
            print(11111111111111111, user)
            quiz = Quiz(quiz, user[0])
            db.session.add(quiz)
            db.session.commit()
        else:
            question = request.form.get('question')
            answer = request.form.get('answer')
            wrong1 = request.form.get('wrong1')
            wrong2 = request.form.get('wrong2')
            wrong3 = request.form.get('wrong3')
            if all([question, answer, wrong1, wrong2, wrong3]):
                q = Question(question, answer, wrong1, wrong2, wrong3)
                db.session.add(q)
                db.session.commit()
        return redirect(url_for('view_quiz_edit', qqq='123'))
    quizes = Quiz.query.all()
    questions = Question.query.all()
    return render_template('quizes_view.html',
                           html_config = html_config,
                           quizes = quizes,
                           questions = questions,
                           len = len)

@app.route('/quiz_edit/<int:id>', methods = ['GET', 'POST'])
def quiz_edit(id):
    # если POST - значит ответ от формы
    if request.method == 'POST':
        quiz = Quiz.query.get(id)
        if quiz:
            if request.form.get('name') and len(request.form.get('name')) > 3:
                quiz.name = request.form.get('name')
                db.session.commit()
            
            #составляем списки вопросов для удаления и добавления отмеченные в форме
            add_q = [q[1] for q in request.form.items() if q[0][:6]=='check2']
            del_q = [q[1] for q in request.form.items() if q[0][:6]=='check1']

            # добавляем вопросы - вариант1            
            # for q in add_q:
            #     quiz.question.append(Question.query.get(int(q))) 

            if add_q or del_q:
                # добавляем вопросы - вариант2
                qs = Question.query.filter(Question.id.in_(add_q)).all()
                for q in qs:
                    quiz.question.append(q)

                # удаляем  вопросы
                for q in del_q:
                    quiz.question.remove(Question.query.get(int(q)))

                db.session.commit()
            return redirect('/quizes_view/')
        
    # если GET
    quiz = Quiz.query.filter_by(id=id).one()
    q_ids = [q.id for q in quiz.question] #список id вопросов которые вошли в этот КВИЗ
    questions = Question.query.filter(Question.id.not_in(q_ids)) # выборка вопросов которые не вошли
    return render_template('quiz_edit.html',
                           quiz = quiz,
                           no_questions = questions,
                           html_config = html_config)

# удаление квиза
@app.route('/quiz_delete/<int:id>/', methods = ['GET', 'POST'])
def quiz_delete(id):
    Quiz.query.filter_by(id = id).delete()
    db.session.commit()
    return redirect('/quizes_view/')

# удаление вопроса
@app.route('/question_delete/<int:id>/', methods = ['GET', 'POST'])
def question_delete(id):
    Question.query.filter_by(id = id).delete()
    db.session.commit()
    return redirect('/quizes_view/')

# редактирование вопроса
@app.route('/question_edit/<int:id>/', methods = ['GET', 'POST'])
def qeustion_edit(id):
    if request.method == 'POST':
        question = request.form.get('question')
        answer = request.form.get('answer')
        wrong1 = request.form.get('wrong1')
        wrong2 = request.form.get('wrong2')
        wrong3 = request.form.get('wrong3')
        q:Question = Question.query.filter_by(id = id).one()
        if all([question, answer, wrong1, wrong2, wrong3, q]):
            q.question = question
            q.answer = answer
            q.wrong1 = wrong1
            q.wrong2 = wrong2
            q.wrong3 = wrong3
            db.session.commit()
        return redirect('/quizes_view/')
    q = Question.query.filter_by(id = id).one()
    return render_template('question_edit.html', 
                           q = q,
                           html_config = html_config)

# достаем из текущей сессии login, и находим по нему Имя Фамилию
@app.before_request
def get_user():
    if 'logged_in' in session:
        for user in users.values():
            if user['login'] == session['login']:
                g.user = user
                break

# генерим session_id используя hmac, hashlib, time
def generate_session_id(login):
    secret_key = app.config['SECRET_KEY'].encode('utf-8')
    timestamp = str(int(time.time() * 1000000)) # время с микросекундами
    data = f"{login}{timestamp}".encode('utf-8')
    session_id = hmac.new(secret_key, data, hashlib.sha256).hexdigest()
    return session_id

# Декоратор с переадресацией если пользователь не залогинен
def login_required(func):
    def wrapper(*args, **kwargs):
        if not is_logged_in():
            return redirect(url_for('login_form'))
        return func(*args, **kwargs)
    # ВАЖНО!!! каждый раз переименовываем имя функции, иначе ошибка
    wrapper.__name__ = func.__name__
    return wrapper

# Главная страница
@app.route("/")
# @login_required
def index():
    
    return render_template('index.html')

# ДЗ 5 - HTML тэги
@app.route("/html_tags/")
@login_required
def html_tags():
    return render_template('html_tags.html')

# ДЗ 6 - форма регистрации на работу
@app.route("/job_application_form/")
@login_required
def job_application_form():
    return render_template('job_application_form.html')

# Случайная утка
@app.route('/duck/')
@login_required
def duck():
    try:
        server_reply = requests.get('https://random-d.uk/api/v2/random')
        data = server_reply.json()
        print(data)
        return render_template('duck.html', 
                               image_url=data['url'],
                               duck_id=data['url'].split('/')[-1].split('.')[0])
    except Exception as e:
        return f"Ошибка в модуле уток: {str(e)}", 500

# Случайные лисы
@app.route('/fox/<int:num>/')
@login_required
def fox(num):
    if not 1 <= num <= 10:
        return "Допускается от 1 до 10 лис", 400
    foxes = []
    for _ in range(num):
        server_reply = requests.get('https://randomfox.ca/floof/')
        foxes.append(server_reply.json()['image'])
    return render_template('fox.html', foxes=foxes)

# Погода в Минске
@app.route('/weather_minsk/')
@login_required
def weather_minsk():
    return weather('Minsk')

# метод получения города из формы для погоды
@app.route('/weather/', methods=['GET', 'POST'])
@login_required
def enter_city_name():
    if request.method == 'POST':
        city = request.form.get('city')
        print(city)
        return redirect(url_for('weather', city=city))
    return render_template('city_form.html')

# Погода для заданного города
@app.route('/weather/<city>/')
@login_required
def weather(city):
    try:
        server_reply = requests.get(
            f'http://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric&lang=ru')
        data = server_reply.json()

        if server_reply.status_code != 200:
            return f"Ошибка: {data['message']}", 404
        
        weather_data = {
            'city': data['name'],
            'temp': data['main']['temp'],
            'feels_like': data['main']['feels_like'],
            'description': data['weather'][0]['description'].capitalize(),
            'icon': data['weather'][0]['icon']
        }
        return render_template('weather.html', weather_data=weather_data)
    except Exception as e:
        return f'Ошибка в модуле погоды: {str(e)}', 500

# обработчик ошибок
@app.errorhandler(404)
def not_found(error):
    return render_template('404.html')

# форма для логина
@app.route("/login/", methods=['GET', 'POST'])
def login_form():
    if request.method == 'POST':
        login = request.form.get('login').strip()
        password = request.form.get('password').strip()

        # Проверяем, есть ли такой пользователь
        result = validate_login_data(login, password)
        if 'error' in result:
            return render_template('login.html',
                            error=result['error'],
                            filled_login=result['filled_login'])
        else:
            login_user(login)
            return redirect(url_for('index'))
    
    if 'logged_in' in session:
        return redirect(url_for('index'))
    
    return render_template('login.html')

# валидация данных при логине
def validate_login_data(login, password):
    if not login:
        return {'error':'Логин не может быть пустым', 
                'filled_login':login}
    
    for user in users.values():
            if user['login'] == login:
                if not password:
                    return {'error':'Пароль не может быть пустым', 
                            'filled_login':login}
                if user['password'] == password:
                    return {'logged_in':True,
                            'login':login}
                else:
                    return {'error':'Неправильный пароль',
                            'filled_login':login}
            else:
                return {'error':'Такого пользователя не существует', 
                'filled_login':login}      

# Логиним пользователя    
def login_user(login):
    session['logged_in'] = True
    session['login'] = login
    session['session_id'] = generate_session_id(login)
    print(session)
    
# Проверка залогинился ли пользователь
def is_logged_in():
    return 'logged_in' in session

# Выход из системы
@app.route('/logout/')
def logout():
    session.clear()
    return redirect(url_for('login_form'))

# обработка данных из формы для регистрации
@app.route('/register/', methods=['GET', 'POST'])
def register_form():
    if request.method == 'POST':
        first_name = request.form.get('first_name').strip()
        last_name = request.form.get('last_name').strip()
        login = request.form.get('login').strip()
        password = request.form.get('password').strip()
        email = request.form.get('email').strip()
        age = request.form.get('age').strip()


        errors, filled_fields = validate_user_data(first_name, last_name, login,
                                              password, email, age)
        print(errors)
        print(filled_fields)
        if errors:
            # если есть ошибки - показать ошибки
            return render_template('register.html',
                                    errors=errors,
                                    filled_fields=filled_fields)
        else:
            # если нет ошибок - добавим пользователя
            add_user(first_name, last_name, login, password, email, age)
            return render_template('success.html')

    return render_template('register.html', 
                           errors={}, 
                           filled_fields={})

# валидация данных при регистрации пользователя
def validate_user_data(first_name, last_name, login, password, email, age):
    errors = {}
    filled_fields = {}
    fields = {
        'first_name': (first_name, is_valid_name),
        'last_name': (last_name, is_valid_name),
        'login': (login, is_valid_login),
        'password': (password, is_valid_password),
        'email': (email, is_valid_email),
        'age': (age, is_valid_age)
    }

    for field_name, (field_value, validation_func) in fields.items():
        try:
            validation_func(field_value)
            filled_fields[field_name] = field_value
        except ValueError as e:
            errors[field_name] = str(e)

    return errors, filled_fields

# добавление нового пользователя
def add_user(first_name, last_name, login, password, email, age):
    global user_id
    global users
    users[user_id] = {
        'first_name': first_name,
        'last_name': last_name,
        'login': login,
        'password': password,
        'email': email,
        'age': age
    }
    user_id += 1

# проверка валидности имени и фамилии
def is_valid_name(name:str):
    if not name:
        raise ValueError(empty_field)
    if not re.match(r"^[а-яА-Я]+$", name):
        raise ValueError('Допустимы только русские буквы.')
    
# проверка валидности логина
def is_valid_login(login:str):
    if not login:
        raise ValueError(empty_field)
    if not re.match(r"^[0-9a-zA-Z_]{6,20}$", login):
        raise ValueError('Допустимы латинские буквы, цифры и знак _')
    # есть ли пользователь с таким логином?
    for user in users.values():
        if user['login'] == login:
            raise ValueError('Пользователь с таким логином уже зарегистрирован')
    
# проверка валидности пароля
def is_valid_password(password:str):
    if not password:
        raise ValueError(empty_field)
    if not re.match(r"^(?=.*[0-9])(?=.*[a-z])(?=.*[A-Z])[0-9a-zA-Z]{8,15}$", password):
        raise ValueError('Допустимы лат буквы и цифры, обязательно 1 латинская' \
                         ' маленькая, 1 заглавная и  1 цифр. От 8 до 15 символов.')

# проверка валидности email
def is_valid_email(email:str):
    email_pattern = r"^[a-zA-Z0-9._%\-]+@[a-zA-Z0-9-]+(?:\.[a-zA-Z]{2,})+$"
    if not email:
        raise ValueError(empty_field)
    if not re.match(email_pattern, email):
        raise ValueError('Введен некорректный email адрес')
    # есть ли пользователь с таким емейл?
    for user in users.values():
        if user['email'] == email:
            raise ValueError('Пользователь с таким email уже зарегистрирован')
    
# проверка возраста
def is_valid_age(age:int):
    if not age:
        raise ValueError(empty_field)
    try:
        age = int(age)
    except ValueError:
        raise ValueError('Допустимо только целое число')
    if not 12 <= age <= 100:
        raise ValueError('Допустимый возраст от 12 до 100')
    


empty_field="Поле не может быть пустым!"
users = {}
user_id = 1

if __name__ == '__main__':
    add_user(
        first_name='Админ',
        last_name='Админ',
        login='Admin123',
        password='Admin123',
        email='some@email.com',
        age=79
    )
    print(users)

    app.run(debug=True, port=7777, host='0.0.0.0')