"""
Тестирование моделей
"""
import unittest
from models.users import Users_id
from models.currency import CurrencyID
from models.currencies_users import Currencies_users


class TestUsersId(unittest.TestCase):
    """Тестовые случаи для модели Users_id"""

    def test_user_creation_valid(self):
        """Тест создания пользователя с валидными данными."""
        user = Users_id("Анна", 25, "anna@example.com")
        self.assertEqual(user.name, "Анна")
        self.assertEqual(user.age, 25)
        self.assertEqual(user.email, "anna@example.com")

    def test_user_age_setter_valid(self):
        """Тест установки валидного возраста."""
        user = Users_id("Тест", 25, "test@example.com")
        user.age = 30
        self.assertEqual(user.age, 30)

    def test_user_age_setter_invalid_negative(self):
        """Тест установки отрицательного возраста."""
        user = Users_id("Тест", 25, "test@example.com")
        with self.assertRaises(ValueError):
            user.age = -5

    def test_user_email_setter_valid(self):
        """Тест установки валидного email."""
        user = Users_id("Тест", 25, "test@example.com")
        user.email = "test@example.com"
        self.assertEqual(user.email, "test@example.com")


class TestCurrencyID(unittest.TestCase):
    """Тестовые случаи для модели CurrencyID"""

    def test_currency_id_creation_valid(self):
        """Тест создания идентификатора валюты с валидными данными."""
        currency = CurrencyID("USD")
        self.assertEqual(currency.id, "USD")

    def test_currency_id_setter_valid(self):
        """Тест установки валидного кода валюты."""
        currency = CurrencyID("USD")
        currency.id = "EUR"
        self.assertEqual(currency.id, "EUR")

    def test_currency_id_setter_case_conversion(self):
        """Тест автоматического преобразования в верхний регистр при установке."""
        currency = CurrencyID("USD")
        currency.id = "eur"
        self.assertEqual(currency.id, "EUR")

    def test_currency_id_setter_invalid_empty(self):
        """Тест установки пустого кода валюты."""
        currency = CurrencyID("USD")
        with self.assertRaises(ValueError) as context:
            currency.id = ""
        self.assertEqual(str(context.exception), 'длина валюты не может быть меньше 1 символа')


class TestCurrenciesUsers(unittest.TestCase):
    """Тестовые случаи для модели Currencies_users"""

    def test_currencies_users_creation(self):
        """Тест создания связи пользователь-валюта."""
        cu = Currencies_users("Анна")
        self.assertEqual(cu.user, "Анна")
        self.assertEqual(cu.currencies, [])

    def test_currencies_users_creation_with_list(self):
        """Тест создания связи с начальным списком валют."""
        cu = Currencies_users("Иван", ["USD", "EUR"])
        self.assertEqual(cu.user, "Иван")
        self.assertEqual(cu.currencies, ["USD", "EUR"])

    def test_user_setter_valid(self):
        """Тест установки валидного имени пользователя."""
        cu = Currencies_users("СтароеИмя")
        cu.user = "НовоеИмя"
        self.assertEqual(cu.user, "НовоеИмя")

    def test_add_currency(self):
        """Тест добавления валюты в список."""
        cu = Currencies_users("Анна")
        cu.add_currency("USD")
        self.assertEqual(cu.currencies, ["USD"])

        # добавление той же валюты не должно дублироваться
        cu.add_currency("USD")
        self.assertEqual(cu.currencies, ["USD"])

if __name__ == '__main__':
    unittest.main()