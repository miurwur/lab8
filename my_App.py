# #localhost:8080/
from models import Users_id, CurrencyID, get_currencies, Currencies_users
from urllib.parse import parse_qs
import requests
from jinja2 import Environment, PackageLoader, select_autoescape
from http.server import HTTPServer, BaseHTTPRequestHandler

# Хранение пользователей и просмотренных ими валют
users_storage = {}

# Навигационное меню
NAVIGATION = [
    {"caption": "Главная", "href": "/"},
    {"caption": "Курсы валют", "href": "/currency"},
    {"caption": "Пользователи и валюты", "href": "/users_currencies"}
]

# Настройка Jinja2
env = Environment(
    loader=PackageLoader("my_App"),
    autoescape=select_autoescape()
)


class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    """Обработчик HTTP запросов"""

    user_data = None

    def do_GET(self):
        """Обработка GET запросов"""
        if self.path == '/':
            self.show_main_page()
        elif self.path == '/users_currencies':
            self.show_users_currencies_page()
        elif self.path == '/currency':
            self.show_currency_input_page()
        elif self.path.startswith('/currency/'):
            self.show_currency_detail_page()
        else:
            self.send_error(404, "Страница не найдена")

    def do_POST(self):
        """Обработка POST запросов"""
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length).decode('utf-8')
        data = parse_qs(post_data)

        if self.path == '/submit':
            self.handle_user_submit(data)
        elif self.path == '/add_currency':
            self.handle_add_currency(data)
        elif self.path == '/currency_submit':
            self.handle_currency_submit(data)
        else:
            self.send_error(404)

    def show_main_page(self, error=None):
        """Показать главную страницу"""
        template = env.get_template("page1.html")
        result = template.render(
            title="Введите ваши данные",
            user_data=None,
            error=error
        )
        self.send_html_response(result)

    def show_users_currencies_page(self, error=None):
        """Показать страницу пользователей и валют"""
        users_data = [
            {
                "username": username,
                "currencies": user_obj.get_currencies()
            }
            for username, user_obj in users_storage.items()
        ]

        template = env.get_template("currencies_users.html")
        result = template.render(
            title="Пользователи и валюты",
            navigation=NAVIGATION,
            users_data=users_data,
            error=error
        )
        self.send_html_response(result)

    def show_currency_input_page(self, error=None):
        """Показать страницу ввода кода валюты"""
        template = env.get_template("currency_input.html")
        result = template.render(
            title="Курсы валют",
            navigation=NAVIGATION,
            error=error
        )
        self.send_html_response(result)

    def show_currency_detail_page(self):
        """Показать детальную информацию о валюте"""
        try:
            currency_id = self.path.split('/')[-1]
            currency_obj = CurrencyID(currency_id)

            # Сохраняем валюту для текущего пользователя
            self.save_currency_for_user(currency_id)

            # Получаем данные по валюте
            currency_data = get_currencies([currency_obj.id])

            if currency_data and currency_obj.id in currency_data:
                currency_info = currency_data[currency_obj.id]
                self.render_currency_success(currency_obj.id, currency_info)
            else:
                self.render_currency_error(currency_obj.id, 'Данные по валюте не получены')

        except ValueError as e:
            self.render_currency_error(currency_id, str(e))
        except requests.exceptions.RequestException:
            self.render_currency_error(currency_id, 'Ошибка при получении данных с сервера')

    def handle_user_submit(self, data):
        """Обработать отправку данных пользователя"""
        try:
            name = data['name'][0]
            age = int(data['age'][0])
            email = data['email'][0]

            self.user_data = Users_id(name, age, email)
            self.redirect('/currency')

        except ValueError as e:
            self.show_main_page(error=str(e))

    def handle_add_currency(self, data):
        """Обработать добавление валюты для пользователя"""
        try:
            username = data['username'][0]
            currency = data['currency'][0].strip().upper()

            if username not in users_storage:
                users_storage[username] = Currencies_users(username)

            users_storage[username].add_currency(currency)
            self.redirect('/users_currencies')

        except Exception as e:
            self.show_users_currencies_page(error=str(e))

    def handle_currency_submit(self, data):
        """Обработать отправку кода валюты"""
        try:
            currency_code = data['currency_code'][0].strip()
            currency_obj = CurrencyID(currency_code)
            self.redirect(f'/currency/{currency_obj.id}')

        except ValueError as e:
            self.show_currency_input_page(error=str(e))

    def save_currency_for_user(self, currency_id):
        """Сохранить валюту для текущего пользователя"""
        if self.user_data and hasattr(self.user_data, 'name'):
            username = self.user_data.name
            if username not in users_storage:
                users_storage[username] = Currencies_users(username)
            users_storage[username].add_currency(currency_id)

    def render_currency_success(self, currency_id, currency_info):
        """Рендерить успешный результат для валюты"""
        template = env.get_template("currency_result.html")
        result = template.render(
            title=f"Курс {currency_id}",
            navigation=NAVIGATION,
            currency_id=currency_id,
            currency_name=currency_info['name'],
            rate=currency_info['value'],
            nominal=currency_info['nominal'],
            error=None
        )
        self.send_html_response(result)

    def render_currency_error(self, currency_id, error_message):
        """Рендерить ошибку для валюты"""
        template = env.get_template("currency_result.html")
        result = template.render(
            title="Ошибка",
            navigation=NAVIGATION,
            currency_id=currency_id,
            error=error_message
        )
        self.send_html_response(result)

    def send_html_response(self, content):
        """Отправить HTML ответ"""
        self.send_response(200)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(bytes(content, "utf-8"))

    def redirect(self, location):
        """Перенаправить на другую страницу"""
        self.send_response(302)
        self.send_header('Location', location)
        self.end_headers()


def run_server():
    """Запустить сервер"""
    httpd = HTTPServer(('localhost', 8080), SimpleHTTPRequestHandler)
    print('Server is running at http://localhost:8080/')
    httpd.serve_forever()


if __name__ == "__main__":
    run_server()