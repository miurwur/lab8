import requests
import sys

class Currencies_users():
    def __init__(self, user: str, currencies: list = None):
        # конструктор
        self.__user = user
        self.__currencies = currencies if currencies is not None else []

    @property
    def user(self):
        return self.__user

    @user.setter
    def user(self, user: str):
        if len(user) >= 1:
            self.__user = user

    @property
    def currencies(self):
        return self.__currencies

    def add_currency(self, currency: str):
        """Добавить валюту в список просмотренных"""
        if currency not in self.__currencies:
            self.__currencies.append(currency)

    def remove_currency(self, currency: str):
        """Удалить валюту из списка"""
        if currency in self.__currencies:
            self.__currencies.remove(currency)

    def get_currencies(self):
        """Получить список всех валют пользователя """
        return self.__currencies

    def clear_currencies(self):
        """Очистить историю валют"""
        self.__currencies.clear()