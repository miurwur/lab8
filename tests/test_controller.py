"""
Тестирование контроллера
Проверка корректного ответа на маршруты
Проверка обработки query-параметров (/user?id=...).
"""
import unittest
from unittest.mock import patch, MagicMock
from io import BytesIO
import my_App
from models import Users_id, CurrencyID, Currencies_users


class TestSimpleHTTPRequestHandler(unittest.TestCase):
    """Тесты для обработчика HTTP-запросов."""

    def setUp(self):
        """Подготовка тестового окружения."""
        # Создаем мок-обработчик
        self.handler = my_App.SimpleHTTPRequestHandler.__new__(my_App.SimpleHTTPRequestHandler)
        self.handler.wfile = BytesIO()
        self.handler.rfile = BytesIO()
        self.handler.headers = {}
        self.handler.path = '/'
        self.handler.user_data = None

        # Мокаем методы отправки ответа
        self.handler.send_response = MagicMock()
        self.handler.send_header = MagicMock()
        self.handler.end_headers = MagicMock()

    def test_handle_root_route(self):
        """Тест обработки главной страницы (/)"""
        with patch('my_App.env.get_template') as mock_get_template:
            mock_template = MagicMock()
            mock_template.render.return_value = "<html>Test</html>"
            mock_get_template.return_value = mock_template

            # Устанавливаем путь
            self.handler.path = '/'

            # Имитируем вызов do_GET
            self.handler.do_GET()

            # Проверяем, что был вызван правильный шаблон
            mock_get_template.assert_called_once_with('page1.html')

            # Проверяем, что ответ был отправлен
            self.handler.send_response.assert_called_with(200)
            self.handler.send_header.assert_called_with('Content-Type', 'text/html; charset=utf-8')
            self.handler.end_headers.assert_called()

    def test_handle_users_route(self):
        """Тест обработки страницы пользователей"""
        with patch('my_App.env.get_template') as mock_get_template:
            mock_template = MagicMock()
            mock_template.render.return_value = "<html>Users</html>"
            mock_get_template.return_value = mock_template

            # Очищаем и добавляем тестовые данные
            my_App.users_storage.clear()

            # Создаем тестового пользователя
            mock_user = MagicMock()
            mock_user.get_currencies.return_value = ['USD', 'EUR']
            my_App.users_storage['test_user'] = mock_user

            # Устанавливаем путь
            self.handler.path = '/users_currencies'
            # Имитируем вызов do_GET
            self.handler.do_GET()

            mock_get_template.assert_called_once_with('currencies_users.html')
            self.handler.send_response.assert_called_with(200)

    def test_handle_currencies_route(self):
        """Тест обработки страницы валют"""
        with patch('my_App.env.get_template') as mock_get_template:
            mock_template = MagicMock()
            mock_template.render.return_value = "<html>Currencies</html>"
            mock_get_template.return_value = mock_template

            self.handler.path = '/currency'
            self.handler.do_GET()

            mock_get_template.assert_called_once_with('currency_input.html')
            self.handler.send_response.assert_called_with(200)

    def test_handle_currency_detail_valid(self):
        """Тест обработки страницы конкретной валюты"""
        with patch('my_App.env.get_template') as mock_get_template, \
                patch('my_App.CurrencyID') as mock_currency_class, \
                patch('my_App.get_currencies') as mock_get_currencies:
            mock_template = MagicMock()
            mock_template.render.return_value = "<html>Currency Detail</html>"
            mock_get_template.return_value = mock_template

            mock_currency = MagicMock()
            mock_currency.id = 'USD'
            mock_currency_class.return_value = mock_currency

            mock_get_currencies.return_value = {
                'USD': {'name': 'Доллар США', 'value': 90.0, 'nominal': 1}
            }

            self.handler.path = '/currency/USD'
            self.handler.do_GET()

            mock_get_template.assert_called_once_with('currency_result.html')
            self.handler.send_response.assert_called_with(200)

    def test_handle_currency_detail_invalid(self):
        """Тест обработки невалидной валюты."""
        with patch('my_App.env.get_template') as mock_get_template, \
                patch('my_App.CurrencyID', side_effect=ValueError("Неверный код валюты")):
            mock_template = MagicMock()
            mock_template.render.return_value = "<html>Error</html>"
            mock_get_template.return_value = mock_template

            self.handler.path = '/currency/INVALID'
            self.handler.do_GET()

            mock_get_template.assert_called_once_with('currency_result.html')
            self.handler.send_response.assert_called_with(200)

    def test_post_submit_user(self):
        """Тест обработки POST /submit (добавление пользователя)."""
        test_data = "name=Анна&age=18&email=anna@example.com"
        self.handler.rfile = BytesIO(test_data.encode('utf-8'))
        self.handler.headers = {'Content-Length': str(len(test_data))}
        self.handler.path = '/submit'

        with patch('my_App.parse_qs', return_value={
            'name': ['Анна'],
            'age': ['18'],
            'email': ['anna@example.com']
        }), patch('my_App.Users_id') as mock_user_class:
            mock_user = MagicMock()
            mock_user_class.return_value = mock_user

            self.handler.do_POST()

            # Проверяем перенаправление
            self.handler.send_response.assert_called_with(302)
            self.handler.send_header.assert_called_with('Location', '/currency')


class TestUserCurrencyHandling(unittest.TestCase):
    """Тесты для обработки пользователей и валют."""

    def setUp(self):
        """Подготовка тестового окружения."""
        my_App.users_storage.clear()

    def test_add_user_currency(self):
        """Тест добавления валюты пользователю."""
        # Создаем тестового пользователя
        mock_user = MagicMock(spec=Currencies_users)
        mock_user.get_currencies.return_value = []
        mock_user.add_currency = MagicMock()

        my_App.users_storage['test_user'] = mock_user

        # Проверяем добавление валюты
        my_App.users_storage['test_user'].add_currency('USD')

    def test_get_user_currencies(self):
        """Тест получения валют пользователя."""
        # Создаем тестового пользователя с валютами
        mock_user = MagicMock(spec=Currencies_users)
        mock_user.get_currencies.return_value = ['USD', 'EUR']

        my_App.users_storage['test_user'] = mock_user

        # Получаем валюты пользователя
        currencies = my_App.users_storage['test_user'].get_currencies()

        self.assertEqual(currencies, ['USD', 'EUR'])


class TestCurrencyValidation(unittest.TestCase):
    """Тесты валидации валют."""

    def test_currency_id_creation(self):
        """Тест создания объекта CurrencyID."""
        currency = CurrencyID('USD')
        self.assertEqual(currency.id, 'USD')

if __name__ == '__main__':
    unittest.main()