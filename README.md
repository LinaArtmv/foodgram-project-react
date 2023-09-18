# Проект Foodgram

### Описание
Проект "Foodgram" – это "продуктовый помощник". На этом сервисе авторизированные пользователи могут публиковать рецепты, подписываться на публикации других пользователей, добавлять понравившиеся рецепты в список «Избранное», а перед походом в магазин скачивать сводный список продуктов, необходимых для приготовления одного или нескольких выбранных блюд. Для неавторизированных пользователей доступны просмотр рецептов и страниц авторов.

Продуктовый помощник - это дипломный проект курса Backend-разработки Яндекс.Практикум и представляет собой онлайн-сервис и API для него.

### Tехнологии
- [Python 3.10](https://www.python.org/downloads/)
- [Django 3.2](https://www.djangoproject.com/)
- [Django Rest Framewok 3.12](https://www.django-rest-framework.org/)
- [PostgreSQL](https://postgrespro.ru/docs/postgresql)


### Локальный запуск проекта в Докер-контейнерах:

Клонировать репозиторий и перейти в него в командной строке:

``` git@github.com:LinaArtmv/foodgram-project-react.git ``` 
``` cd foodgram-project-react ``` 

Запустить docker-compose:

```
docker-compose up

```

После окончания сборки контейнеров выполнить миграции:

```
docker-compose exec backend python manage.py migrate

```

Создать суперпользователя:

```
docker-compose exec backend python manage.py createsuperuser

```

Загрузить статику:

```
docker-compose exec backend python manage.py collectstatic --no-input 

```

Проверить работу проекта по ссылке:

```
http://localhost/
```


### Локальный запуск проекта:

Клонировать репозиторий и перейти в него в командной строке:

``` git@github.com:LinaArtmv/foodgram-project-react.git ``` 
``` cd foodgram-project-react ``` 

Создать и активировать виртуальное окружение:

``` python3 -m venv venv ``` 

* Если у вас Linux/macOS:
    ``` source venv/bin/activate ``` 

* Если у вас Windows:
    ``` source venv/Scripts/activate ```
    
``` python3 -m pip install --upgrade pip ``` 

Установить зависимости из файла requirements:

``` pip install -r requirements.txt ``` 

Выполнить миграции:

``` python3 manage.py migrate ``` 

Запустить проект:

``` python3 manage.py runserver ``` 


### Примеры запросов к API и ответов от сервера

- Пример POST-запроса на адрес 
http://127.0.0.1:8000/api/recipes/ для добавления рецепта: 
```
{
    "ingredients": [
        {
            "id": 1123,
            "amount": 10
        }
    ],
    "tags": [
        1,
        2
    ],
    "image": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABAgMAAABieywaAAAACVBMVEUAAAD///9fX1S0ecCAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAACklEQVQImWNoAAAAggCByxOyYQAAAABJRU5ErkJggg==",
    "name": "string",
    "text": "string",
    "cooking_time": 1
}
```

Пример ответа:

```
{
    "id": 0,
    "tags": [
        {
            "id": 0,
            "name": "Завтрак",
            "color": "#E26C2D",
            "slug": "breakfast"
        }
    ],
    "author": {
        "email": "user@example.com",
        "id": 0,
        "username": "string",
        "first_name": "Вася",
        "last_name": "Пупкин",
        "is_subscribed": false
    },
    "ingredients": [
        {
            "id": 0,
            "name": "Картофель отварной",
            "measurement_unit": "г",
            "amount": 1
        }
    ],
    "is_favorited": true,
    "is_in_shopping_cart": true,
    "name": "string",
    "image": "http://foodgram.example.org/media/recipes/images/image.jpeg",
    "text": "string",
    "cooking_time": 1
}
```

- Пример POST-запроса на адрес 
http://127.0.0.1:8000/api/users/ для добавления пользователя: 
```
{
    "email": "vpupkin@yandex.ru",
    "username": "vasya.pupkin",
    "first_name": "Вася",
    "last_name": "Пупкин",
    "password": "Qwerty123"
}
```

- Пример ответа:
```
{
    "email": "vpupkin@yandex.ru",
    "id": 0,
    "username": "vasya.pupkin",
    "first_name": "Вася",
    "last_name": "Пупкин"
}
```

### Проект доступен по адресу http://linaartfoodgram.sytes.net/recipes


### Автор проекта
- Ангелина Артемьева,
github: [LinaArtmv](https://github.com/LinaArtmv)