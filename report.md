**Отчет по лабораторной работе №8**  
Студент: Барыкина Анна  
Группа: P3122  


**Цель работы**  

Создать простое клиент-серверное приложение на Python без серверных фреймворков.
Освоить работу с HTTPServer и маршрутизацию запросов.
Применять шаблонизатор Jinja2 для отображения данных.
Реализовать модели предметной области (User, Currency, UserCurrency, App, Author) с геттерами и сеттерами.
Структурировать код в соответствии с архитектурой MVC.
Получать данные о курсах валют через функцию get_currencies и отображать их пользователям.
Реализовать функциональность подписки пользователей на валюты и отображение динамики их изменения.
Научиться создавать тесты для моделей и серверной логики.

**Описание предметной области**

Приложение для отслеживания курсов валют включает следующие модели:

**users**
name — имя пользователя  
age — возраст пользователя  
email — email пользователя  

**currency**
id — уникальный идентификатор  
num_code — цифровой код   
char_code — символьный код  
name — название валюты  
value — курс  
nominal — номинал  

**currencies_users**
id — уникальный идентификатор  
user_id — внешний ключ к User  
currency_id — внешний ключ к Currency  

**Структура проекта**

my_App/                             # Корневая папка проекта          
├── models/                         # Пакет с моделями данных  
│   ├── __init__.py                # Инициализация пакета моделей  
│   ├── currencies_users.py        # Модель связи пользователей и валют  
│   ├── currency.py                # Модель валюты и работа с API  
│   └── users.py                   # Модель пользователя  
├── templates/                      # HTML шаблоны  
│   ├── currencies_users.html      # Страница истории валют пользователя  
│   ├── currency_input.html        # Страница ввода кода валюты  
│   ├── currency_result.html       # Страница с результатом курса валюты  
│   ├── page1.html                 # Главная страница  
│   └── page2.html                 # Вторая страница  
├── my_App.py                      # Основной файл приложения(веб-сервер)  
└── report.md                      # Отчет о проекте  

**Назначение файлов:**

my_App.py - HTTP сервер, обработка запросов, маршрутизация (сontroller)  
models/ - бизнес-логика (model)  
templates/ - HTML шаблоны для отображения (view)  

**Реализация:**

**Геттеры и сеттеры**
Все классы скрывают внутренние данные (приватные поля с __)  
Для доступа к данным используются специальные методы (@property)  
При изменении данных выполняется проверка: если данные неправильные, выдается ошибка  

**HTTP сервер**
Создан обработчик запросов CurrencyRequestHandler
Поддерживаемые адреса:  
/ - Начальная страница  
/users_currencies - Страница с пользователями и валютами
/currency - Страница для ввода кода валюты
/currency/{код_валюты} - Страница с информацией о конкретной валюте  

**Шаблонизатор Jinja2**

Инициализация Environment один раз при старте приложения: 
```python
env = Environment(
    loader=PackageLoader("myapp"),
    autoescape=select_autoescape()
)
```

**Примеры работы приложения**  
Главная страница (/)  
Форма для ввода данных пользователя (имя, возраст, email)  
<img width="2554" height="1311" alt="image" src="https://github.com/user-attachments/assets/ef06a77e-5e54-4bea-88cf-23c24c286e29" />  


Ввод кода валюты (/currency)  
Форма для ввода 3-буквенного кода валюты (USD, EUR, GBP и т.д)  
Проверка корректности кода  
<img width="2560" height="1318" alt="image" src="https://github.com/user-attachments/assets/95b6ea4c-2cfc-4d81-aef5-8973f6c95bc5" />  


Просмотр курса валюты (/currency/{код})  
Детальная информация о выбранной валюте  
Текущий курс к рублю  
Номинал валюты  
<img width="2560" height="1294" alt="image" src="https://github.com/user-attachments/assets/f6dd9fec-4e32-4fb3-acaf-7b4627a573b9" />  


Пользователи и валюты (/users_currencies)
Список всех пользователей и просмотренных ими валют
Возможность добавления валют пользователям
<img width="2558" height="1306" alt="image" src="https://github.com/user-attachments/assets/50f5e86d-579c-408d-a7e6-7334fc457d43" />  


**Тестирование**  

Пример теста для модели: 
```python
    def test_user_creation_valid(self):
        """Тест создания пользователя с валидными данными."""
        user = Users_id("Анна", 25, "anna@example.com")
        self.assertEqual(user.name, "Анна")
        self.assertEqual(user.age, 25)
        self.assertEqual(user.email, "anna@example.com")
```

Пример теста для контроллера:  
```python
def test_handle_root_route(self):
    """Тест обработки главной страницы (/)"""
    # 1. Патчим метод получения шаблонов из окружения Jinja2
    with patch('my_App.env.get_template') as mock_get_template:
        # 2. Создаем мок-объект шаблона
        mock_template = MagicMock()
        # 3. Настраиваем возвращаемое значение метода render()
        mock_template.render.return_value = "<html>Test</html>"
        
        # 4. Настраиваем, что get_template() возвращает наш мок-шаблон
        mock_get_template.return_value = mock_template

        # 5. Устанавливаем тестовый путь (маршрут главной страницы)
        self.handler.path = '/'
        
        # 6. Имитируем вызов метода обработки GET-запроса
        self.handler.do_GET()

        # 7. ПРОВЕРКА: убеждаемся, что был вызван правильный шаблон
        mock_get_template.assert_called_once_with('page1.html')
        
        # 8. ПРОВЕРКА: убеждаемся, что отправлен успешный статус 200
        self.handler.send_response.assert_called_with(200)
        
        # 9. ПРОВЕРКА: убеждаемся, что установлен правильный Content-Type
        self.handler.send_header.assert_called_with(
            'Content-Type', 'text/html; charset=utf-8'
        )
```

