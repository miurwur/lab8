# #localhost:8080/
from models import Users_id
from models import Users_id
from models import CurrencyID, get_currencies
from models import Currencies_users
users_storage = {} # Хранение пользователей и просмотренных ими валют

from urllib.parse import parse_qs
import requests
import sys
import io


from jinja2 import Environment, PackageLoader, select_autoescape

from http.server import HTTPServer, BaseHTTPRequestHandler


# Навигационное меню для страницы 2
NAVIGATION_page2 = [
    {"caption": "Главная", "href": "/"},
    {"caption": "Курсы валют", "href": "/currency"},
    {"caption": "Пользователи и валюты", "href": "/users_currencies"}
]

# Настройка среды Jinja2 для шаблонов
env = Environment(
    loader=PackageLoader("my_App"),
    autoescape=select_autoescape()
)


class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    """
    Обработчик HTTP запросов
    """

    user_data = None

    def do_GET(self):
        """
         do_GET: обрабатывает все GET запросы к серверу в
         зависимости от пути (self.path) возвращает соответствующую страницу
        """

        self.send_response(200)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.end_headers()

        # Обрабатываем разные URL
        if self.path == '/':
            # Главная страница: форма ввода данных пользователя
            template = env.get_template("page1.html")
            result = template.render(title="Введите ваши данные",
                    user_data = None)
            self.wfile.write(bytes(result, "utf-8"))


        elif self.path == '/users_currencies':


            ''' Страница с пользователями и валютами'''
            template = env.get_template("currencies_users.html")

            users_data = []
            for username, user_obj in users_storage.items():
                users_data.append({
                    "username":username,
                    "currencies": user_obj.get_currencies()
                })

            result = template.render(
                title="Пользователи и валюты",
                navigation=NAVIGATION_page2,
                users_data=users_data,
                error=None
            )
            self.wfile.write(bytes(result, "utf-8"))

        elif self.path == '/currency':
            # Страница для ввода кода валюты
            template = env.get_template("currency_input.html")
            result = template.render(
                title="Курсы валют",
                navigation=NAVIGATION_page2,
                error=None
            )
            self.wfile.write(bytes(result, "utf-8"))

        elif self.path.startswith('/currency/'):
            # Страница с курсом конкретной валюты
            try:
                # Извлекаем ID валюты через URL и создаем новый объект(пример: CurrencyID(USD))
                currency_id = self.path.split('/')[-1]
                currency_obj = CurrencyID(currency_id)

                # Сохраняем валюту для текущего пользователя
                if self.user_data and hasattr(self.user_data, 'name'):
                    username = self.user_data.name
                    if username not in users_storage:
                        users_storage[username] = Currencies_users(username)
                    users_storage[username].add_currency(currency_id)

                # Получаем данные по валюте
                currency_data = get_currencies([currency_obj.id])

                template = env.get_template("currency_result.html")

                if currency_data and currency_obj.id in currency_data:
                    currency_info = currency_data[currency_obj.id]

                    # if isinstance(currency_info, str):  # если валюта не в виде словаря, то возвращаем ошибку
                    #     result = template.render(
                    #         title=f"Курс {currency_obj.id}",
                    #         navigation=NAVIGATION_page2,
                    #         currency_id=currency_obj.id,
                    #         error=currency_info
                    #     )
                    # else:
                    # Успешное получение данных о валюте
                    result = template.render(
                        title=f"Курс {currency_obj.id}",
                        navigation=NAVIGATION_page2,
                        currency_id=currency_obj.id,
                        currency_name=currency_info['name'],
                        rate=currency_info['value'],
                        nominal=currency_info['nominal'],
                        error=None
                    )
                else:
                    # Если данные по валюте не найдены
                    result = template.render(
                        title=f"Курс {currency_obj.id}",
                        navigation=NAVIGATION_page2,
                        currency_id=currency_obj.id,
                        error='Данные по валюте не получены'
                    )

                self.wfile.write(bytes(result, "utf-8"))

            except ValueError as e:
                # Ошибка валидации кода валюты
                template = env.get_template("currency_result.html")
                result = template.render(
                    title="Ошибка",
                    navigation=NAVIGATION_page2,
                    currency_id=currency_id,
                    error=str(e)
                )
                self.wfile.write(bytes(result, "utf-8"))

            except requests.exceptions.RequestException as e:
                # Ошибка сети при запросе к API курсов валют
                template = env.get_template("currency_result.html")
                result = template.render(
                    title="Ошибка",
                    navigation=NAVIGATION_page2,
                    currency_id=currency_id,
                    error='Ошибка при получении данных с сервера'
                )
                self.wfile.write(bytes(result, "utf-8"))



    def do_POST(self):
        """
        Обрабатывает все POST запросы к серверу.
        Включает обработку форм пользователя и запросов курсов валют.
        """
        if self.path == '/submit':
            try:
                content_length = int(self.headers['Content-Length'])
                post_data = self.rfile.read(content_length).decode('utf-8')
                data = parse_qs(post_data)

                name = data['name'][0]
                age = int(data['age'][0])
                email = data['email'][0]

                self.user_data = Users_id(name, age, email)

                self.send_response(302)
                self.send_header('Location', '/currency')
                self.end_headers()

            except ValueError as e:
                # Показываем форму снова с сообщением об ошибке
                template = env.get_template("page1.html")
                result = template.render(
                    title="Введите ваши данные",
                    user_data=None,
                    error=str(e)  # Передаем сообщение об ошибке в шаблон
                )
                self.send_response(200)
                self.send_header('Content-Type', 'text/html; charset=utf-8')
                self.end_headers()
                self.wfile.write(bytes(result, "utf-8"))
                return


        elif self.path == '/add_currency':
            # Обработка добавления валюты для пользователя
            try:
                content_length = int(self.headers['Content-Length'])
                post_data = self.rfile.read(content_length).decode('utf-8')
                data = parse_qs(post_data)

                username = data['username'][0]
                currency = data['currency'][0].strip().upper()

                # Добавляем пользователя
                if username not in users_storage:
                    users_storage[username] = Currencies_users(username)

                # Добавляем валюту
                users_storage[username].add_currency(currency)

                # Перенаправляем обратно на страницу пользователей
                self.send_response(302)
                self.send_header('Location', '/users_currencies')
                self.end_headers()

            except Exception as e:
                # В случае ошибки показываем страницу с сообщением об ошибке
                template = env.get_template("users_currencies.html")
                users_data = []
                for username, user_obj in users_storage.items():
                    users_data.append({
                        "username": username,
                        "currencies": user_obj.get_currencies()
                    })

                result = template.render(
                    title="Пользователи и валюты",
                    navigation=NAVIGATION_page2,
                    users_data=users_data,
                    error=str(e)
                )
                self.send_response(200)
                self.send_header('Content-Type', 'text/html; charset=utf-8')
                self.end_headers()
                self.wfile.write(bytes(result, "utf-8"))

        elif self.path == '/currency_submit':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length).decode('utf-8')
            data = parse_qs(post_data)

            currency_code = data['currency_code'][0].strip()

            try:
                currency_obj = CurrencyID(currency_code)
                self.send_response(302)
                self.send_header('Location', f'/currency/{currency_obj.id}')
                self.end_headers()
            except ValueError as e:
                template = env.get_template("currency_input.html")
                result = template.render(
                    title="Курсы валют",
                    navigation=NAVIGATION_page2,
                    error=str(e)
                )
                self.send_response(200)
                self.send_header('Content-Type', 'text/html; charset=utf-8')
                self.end_headers()
                self.wfile.write(bytes(result, "utf-8"))

def run_server():
    httpd = HTTPServer(('localhost', 8080), SimpleHTTPRequestHandler)
    print('server is running')
    httpd.serve_forever()

if __name__ == "__main__":
    run_server()

