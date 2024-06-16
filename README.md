## Описание

Проект Foodgram автоматически собирает образы и формирует контейнеры с помощью GitHub Actions и Docker для
непрерывного CI/CD во время разработки. При каждом 'push' от разработчика, docker собирает образы из 
docker-compose файла и GitHub Actions формирует контейнеры для проверки интегрции и деплоя 
нового 'запушенного' кода на сервере. При удачной проверке, в телеграм приходит уведомление от бота.
## Запустить проект локально

Для того, чтобы запустить прект локально - перейдите вот [сюда](./backend/README.md)

## Адрес проекта

https://kiselevfoodgram.ddns.net/

## Установка

Клонировать репозиторий и перейти в него в командной строке:

```
git clone https://github.com/kirillkiselev-slim/foodgram/
```

Cоздать и активировать виртуальное окружение:

```
python3 -m venv env
```

* Если у вас Linux/macOS

    ```
    source env/bin/activate
    ```

* Если у вас windows

    ```
    source env/scripts/activate
    ```

```
python3 -m pip install --upgrade pip
```

Установить зависимости из файла requirements.txt:

```
cd backend
```

```
pip install -r requirements.txt
```
При редактировании кода, исправления багов или других модификациях, в терминале запустите:
```
cd <директория с файлом>
```

```
git add <имя_файла>
```

```
git commit -m '<ваше_сообщение_с_объяснением_коммита>'
```

```
git push'
```

После всех этих действия, docker соберет образы, а Github Actions проверит ваш новый код.

## Примеры запросов

### 1-ый пример
Method: `Post`
Endpoint: `http://kiselevfoodgram.ddns.net/api/recipes/`

Body: 

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
  "image": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABAgMAAABieywaAAAACVBMVEUAAAD///9fX1/S0ecCAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAACklEQVQImWNoAAAAggCByxOyYQAAAABJRU5ErkJggg==",
  "name": "string",
  "text": "string",
  "cooking_time": 1
}
```

Response: 

```
{
  "id": 0,
  "tags": [
    {
      "id": 0,
      "name": "Завтрак",
      "slug": "breakfast"
    }
  ],
  "author": {
    "email": "user@example.com",
    "id": 0,
    "username": "string",
    "first_name": "Вася",
    "last_name": "Иванов",
    "is_subscribed": false,
    "avatar": "http://foodgram.example.org/media/users/image.png"
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
  "image": "http://foodgram.example.org/media/recipes/images/image.png",
  "text": "string",
  "cooking_time": 1
}
```

Status code: 201
|

### 2-ой пример

Method: `GET`
Endpoint: `http://kiselevfoodgram.ddns.net/api/users/subscriptions/`

Response: 

```
{
  "count": 123,
  "next": "http://foodgram.example.org/api/users/subscriptions/?page=4",
  "previous": "http://foodgram.example.org/api/users/subscriptions/?page=2",
  "results": [
    {
      "email": "user@example.com",
      "id": 0,
      "username": "string",
      "first_name": "Вася",
      "last_name": "Иванов",
      "is_subscribed": true,
      "recipes": [
        {
          "id": 0,
          "name": "string",
          "image": "http://foodgram.example.org/media/recipes/images/image.png",
          "cooking_time": 1
        }
      ],
      "recipes_count": 0,
      "avatar": "http://foodgram.example.org/media/users/image.png"
    }
  ]
}
```

Status code: 200


### 3-й пример

Method: `GET`
Endpoint: `http://fooodgrambykiselev.ddns.net/api/ingredients/`

Response: 

```
[
  {
    "id": 0,
    "name": "Капуста",
    "measurement_unit": "кг"
  }
]
```

Status code: 200

### Workflow

![Deploy badge](https://github.com/kirillkiselev-slim/foodgram/actions/workflows/main.yml/badge.svg)


### Использованные технологии

* Python 3.9
* Django 4.2.13
* Django REST framework 3.14 
* Nginx 
* Docker 
* Postgres

### Автор

[Кирилл Киселев](https://github.com/kirillkiselev-slim)

