from flask import Flask, render_template, redirect, url_for, request
import requests
import os

# работает от корневой папки проекта
# BASE_DIR = os.getcwd()

app = Flask(__name__,
            static_folder=os.path.join(BASE_DIR, 'static'),
            template_folder=os.path.join(BASE_DIR, 'templates'))

# app = Flask(__name__)

WEATHER_API_KEY = 'f23199e2033f9af89297e10d7cec508d'

@app.route("/")
def index():
    # Главная страница
    return render_template('index.html')

@app.route('/duck/')
def duck():
    # Случайная утка
    try:
        server_reply = requests.get('https://random-d.uk/api/v2/random')
        data = server_reply.json()
        return render_template('duck.html', 
                               image_url=data['url'],
                               duck_id=data['url'].split('/')[-1].split('.')[0])
    except Exception as e:
        return f"Ошибка в модуле уток: {str(e)}", 500

@app.route('/fox/<int:num>/')
def fox(num):
    # Случайные лисы
    if not 1 <= num <= 10:
        return "Допускается от 1 до 10 лис", 400
    foxes = []
    for _ in range(num):
        server_reply = requests.get('https://randomfox.ca/floof/')
        foxes.append(server_reply.json()['image'])
    return render_template('fox.html', foxes=foxes)

@app.route('/weather_minsk/')
def weather_minsk():
    # Погода в Минске
    return weather('Minsk')

@app.route('/weather/', methods=['GET', 'POST'])
def enter_city_name():
    if request.method == 'POST':
        city = request.form.get('city')
        print(city)
        return redirect(url_for('weather', city=city))
    return render_template('city_form.html')

@app.route('/weather/<city>/')
def weather(city):
    # Погода для заданного города
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

@app.errorhandler(404)
def not_found(error):
    return render_template('404.html')

if __name__ == '__main__':
    app.run(debug=True, port=7777)