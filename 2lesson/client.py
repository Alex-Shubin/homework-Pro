import socket

def send_command(sock, command):
    sock.send(command.encode())
    print(f"Ответ сервера: {sock.recv(1024).decode()}")

def main():
    HOST = ('127.0.0.1', 7777)
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
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
                login = input("Введите логин: ")
                password = input("Введите пароль: ")
                command = f"command:reg; login:{login}; password:{password}"
                print(f"Регистрация пользователя: {login}")
                send_command(sock, command)
            elif choice == "2":
                login = input("Введите логин: ")
                password = input("Введите пароль: ")
                command = f"command:signin; login:{login}; password:{password}"
                print(f"Вход пользователя: {login}")
                send_command(sock, command)
            elif choice == "3":
                command = f"command:list_users"
                send_command(sock, command)
                # print(sock.recv(1024).decode())
            elif choice == "4":
                print("Выход из программы")
                break
            else:
                print("Пожалуйста, выберите действие из меню")

    except ConnectionRefusedError:
        print("Сервер не доступен")
    except Exception as e:
        print("Ошибка: {e}")
    finally:
        # закрываем соединение
        sock.close()

if __name__ == "__main__":
    main()