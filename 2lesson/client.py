"""

написать приложение-клиент используя модуль socket работающее в домашней 
локальной сети.
Приложение должно соединятся с сервером по известному адрес:порт и отправлять 
туда текстовые данные.

известно что сервер принимает данные следующего формата:
    "command:reg; login:<login>; password:<pass>" - для регистрации пользователя
    "command:signin; login:<login>; password:<pass>" - для входа пользователя
    
    
с помощью программы зарегистрировать несколько пользователей на сервере и произвести вход


"""


import socket

def send_command(sock, command):
    sock.send(command.encode())
    print(f"Ответ сервера: {sock.recv(1024).decode()}")

def register_user(sock):
    login = input("Введите логин: ")
    password = input("Введите пароль: ")
    command = f"command:reg; login:{login}; password:{password}"
    print(f"Регистрация пользователя: {login}")
    send_command(sock, command)

def login_user(sock):
    login = input("Введите логин: ")
    password = input("Введите пароль: ")
    command = f"command:signin; login:{login}; password:{password}"
    print(f"Вход пользователя: {login}")
    send_command(sock, command)

def list_users(sock):
    command = f"command:list_users"
    send_command(sock, command)
    # print(sock.recv(1024).decode())

def disconnect_client(sock):
    command = f"command:disconnect"
    send_command(sock, command)
    print("Выход из программы")

def main():
    HOST = ('127.0.0.1', 7777)
    
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect(HOST)
        print(f"Подключено к {HOST}")

        while True:
            print('\nМеню:')
            print("1. Добавить пользователя")
            print("2. Войти в систему")
            print("3. Вывести список зарегистрированных пользователей")
            print("4. Выход")

            choice = input("Выберите действие: ")

            if choice == "1":
                register_user(sock)
            elif choice == "2":
                login_user(sock)
            elif choice == "3":
                list_users(sock)
            elif choice == "4":
                disconnect_client(sock)
                break
            else:
                print("Пожалуйста, выберите действие из меню")

    except ConnectionRefusedError:
        print("Сервер не доступен")
    except Exception as e:
        print(f"Ошибка: {e}")
    finally:
        # закрываем соединение
        sock.close()

if __name__ == "__main__":
    main()