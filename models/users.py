class Users_id():
    def __init__(self, name: str, age: int, email: str):
        # конструктор
        self.__name = name
        self.__age = age
        self.__email = email

    @property
    def name(self):
        return self.__name

    @name.setter
    def name(self, name: str):
        if len(name) >= 1:
            self.__name = name
        else:
            raise ValueError('Имя не может быть меньше 1 символа')

    @property
    def age(self):
        return self.__age

    @age.setter
    def age(self, age):
        if age > 0:
            self.__age = age
        else:
            raise ValueError('Возраст не может быть меньше 1')

    @property
    def email(self):
        return self.__email

    @email.setter
    def age(self, email):
        if len(email) > 0:
            self.__email = email
        else:
            raise ValueError('длина email не может быть меньше 1')

# основной модуль программы
# import models

main_author = Users_id('Anna Barykina', 18, "eh")
# print(main_author.email)
# print(main_author.name, main_author.group)
# main_author.group = 'P3122'
# print(main_author.name, main_author.group)
