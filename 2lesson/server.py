'''
написать приложение-сервер используя модуль socket работающее в домашней 
локальной сети.
Приложение должно принимать данные с любого устройства в сети отправленные 
или через программу клиент или через браузер
    - если данные пришли по протоколу http создать возможность след.логики:
        - если путь "/" - вывести главную страницу
        
        - если путь содержит /test/<int>/ вывести сообщение - тест с номером int запущен
        
        - если путь содержит message/<login>/<text>/ вывести в консоль/браузер сообщение
            "{дата время} - сообщение от пользователя {login} - {text}"
        
        - если путь содержит указание на файл вывести в браузер этот файл
        
        - во всех остальных случаях вывести сообщение:
            "пришли неизвестные  данные по HTTP - путь такой то"
                   
         
    - если данные пришли НЕ по протоколу http создать возможность след.логики:
        - если пришла строка формата "command:reg; login:<login>; password:<pass>"
            - выполнить проверку:
                login - только латинские символы и цифры, минимум 6 символов
                password - минимум 8 символов, должны быть хоть 1 цифра
            - при успешной проверке:
                1. вывести сообщение на стороне клиента: 
                    "{дата время} - пользователь {login} зарегистрирован"
                2. добавить данные пользователя в список/словарь на сервере
            - если проверка не прошла вывести сообщение на стороне клиента:
                "{дата время} - ошибка регистрации {login} - неверный пароль/логин"
                
        - если пришла строка формата "command:signin; login:<login>; password:<pass>"
            выполнить проверку зарегистрирован ли такой пользователь на сервере:                
            
            при успешной проверке:
                1. вывести сообщение на стороне клиента: 
                    "{дата время} - пользователь {login} произведен вход"
                
            если проверка не прошла вывести сообщение на стороне клиента:
                "{дата время} - ошибка входа {login} - неверный пароль/логин"
        
        - во всех остальных случаях вывести сообщение на стороне клиента:
            "пришли неизвестные  данные - <присланные данные>"       
                 

'''


import socket
import datetime
import re

def send_http(text, conn):
    conn.send(OK + HEADERS_text + text.encode("utf-8"))

def is_file_requested(path):
    if path[-4:] in ['.jpg', '.png', '.gif', '.ico', '.txt'] or \
        path[-5:] in ['.html', '.json']:
        return True
    return False

def send_file_http(file_name, conn):
    try:
        with open('2lesson/'+file_name.lstrip('/'), 'rb') as f:
            conn.send(OK)
            conn.send(HEADERS)
            conn.send(f.read())

    except IOError:
        send_http(f"no such file\n", conn)
        conn.send(ERR_404)
        raise IOError("File not found!")
    
def is_test_requested(path):
    if path.startswith("/test/") and len(path.strip('/').split('/')) >= 2:
        try:
            int(path.strip('/').split('/')[1])
            return True
        except ValueError:
            return False
    return False

def send_test_http(path, conn):
    num = int(path.strip('/').split('/')[1])
    send_http(f"тест с номером {num} запущен", conn)

def is_message_requested(path):
    if path.startswith("/message/") and len(path.strip('/').split('/')) >= 3:
        return True
    return False

def send_message_http(path, conn, users):
    login = path.strip('/').split('/')[1]
    text = path.strip('/').split('/')[2]
    if login in users:
        send_http(f"{datetime_now}" \
                  f" - сообщение от пользователя {login} - {text}", conn)
    else:
        send_http(f"{datetime_now}" \
                  f" - {login} - нет такого пользователя", conn)

def is_http(data):
    return data.startswith("GET") or data.startswith("POST")

def is_command(data):
    if "command" in data:
        return True
    return False
    
def is_register_cmd(data):
    if "reg" in data:
        return True
    
def register_user_cmd(data, conn, users):
    login = data.split(";", 2)[1].strip(" ").split(":")[1]
    password = data.split(";", 2)[2].strip(" ").split(":")[1]
    if validate_and_register(login, password, conn):
        if not is_user_exists(login, users):
            conn.send(f"{datetime_now} - " \
                        f"пользователь {login} зарегистрирован".encode())
            users[login] = password
        else:
            conn.send(f"{datetime_now} - " \
                        f"пользователь {login} уже существует".encode())


def is_signin_cmd(data):
    if "signin" in data:
        return True
    
def signin_user_cmd(data, conn, users):
    login = data.split(";", 2)[1].strip(" ").split(":")[1]
    password = data.split(";", 2)[2].strip(" ").split(":")[1]
    if is_login_correct(login, password, users):
        conn.send(f"{datetime_now} - " \
                    f"пользователь {login} произведен вход".encode())
    else:
        conn.send(f"{datetime_now} - " \
                    f"ошибка входа {login} - " \
                    f"неверный пароль/логин".encode())


def is_valid_login(login:str):
    if not login:
        raise ValueError("Логин не может быть пустым")
    if not re.match(r"^[a-zA-Z0-9]{6,}$", login):
        raise ValueError("Логин не менее 6 английских букв и цифр")
    
    
def is_valid_pass(password:str):
    if not password:
        raise ValueError("Пароль не может быть пустым")
    if not re.match(r"^(?=.*\d)[a-zA-Z0-9]{8,}$", password):
        raise ValueError("Пароль не менее 8 символов, минимум 1 цифра")
    
def validate_and_register(login, password, conn):
    try:
        is_valid_login(login)
        is_valid_pass(password)
        return True
    except ValueError as e:
        conn.send(f"{datetime_now}" \
                  f" - ошибка регистрации {login} {e}".encode())
        return False
    
def is_user_exists(login, users):
    return login in users

def is_login_correct(login, password, users):
    return login in users and users[login] == password

def is_list_users_cmd(data):
    if "list_users" in data:
        return True
    return False

def list_users_cmd(conn, users):
    user_list = "\n".join(users.keys())
    user_list_report = f"{datetime_now} - Список пользователей:\n{user_list}"
    conn.send(user_list_report.encode())

def is_disconnect(data):
    return True if "disconnect" in data else False
    
HOST = ('127.0.0.1', 7777)

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.bind(HOST)
sock.listen()

OK = b'HTTP/1.1 200 OK\n'
HEADERS = b'Host: myhost.by\nHost1: myhost1.by\n\n'
HEADERS_text = b'Content-Type: text/plain; charset=utf-8\n\n'
ERR_404 = b'HTTP/1.1 404 Not Found\n\n'

users = {
    "Admin1":"qwerty12",
    "Vasya1":"123456qw",
    "guest1":""
}
path = ''
datetime_now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

while True:
    print("====Listen====")
    conn, addr = sock.accept()
    
    while True:
        data = conn.recv(1024).decode()
        print(data)

        try:
            if is_http(data): # если запрос пришел по http
                method, path, ver = data.split('\n')[0].split(" ", 2)
                print('http data: ', method, path, ver)
                if path == "/":
                    send_file_http('1.html', conn)
                elif is_test_requested(path):
                    send_test_http(path, conn)
                elif is_message_requested(path):
                    send_message_http(path, conn, users)
                elif is_file_requested(path):
                    send_file_http(path, conn)
                else:
                    send_http(f"пришли неизвестные  данные по HTTP - " \
                        f"{path}", conn)
            elif is_command(data): # если запрос пришел из командной строки
                if is_register_cmd(data): # если запрос на регистрацию
                    register_user_cmd(data, conn, users)
                elif is_signin_cmd(data): # если запрос на логин
                    signin_user_cmd(data, conn, users)
                elif is_list_users_cmd(data): # если запрос на листинг пользователей
                    list_users_cmd(conn, users)
                elif is_disconnect(data):
                    break
            else:
                conn.send(f"пришли неизвестные  данные - {data}".encode())
        except Exception as e:
            print(f'Error: {e}')
    
    conn.close()
