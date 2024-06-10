## Описание

Проект Foodgram автоматически собирает образы и формирует контейнеры с помощью GitHub Actions и Docker для
непрерывного CI/CD во время разработки. При каждом 'push' от разработчика, docker собирает образы из 
docker-compose файла и GitHub Actions формирует контейнеры для проверки интегрции и деплоя 
нового 'запушенного' кода на сервере. При удачной проверке, в телеграм приходит уведомление от бота.

## Адрес проекта

https://foodgrambykiselev.ddns.net/

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

### Workflow

[Deploy badge](https://github.com/kirillkiselev-slim/foodgram/actions/workflows/main.yml/badge.svg)


### Использованные технологии

* Python 3.9
* Django 4.2.13
* Django REST framework 3.14 
* Nginx 
* Docker 
* Postgres

### Автор

[Кирилл Киселев](https://github.com/kirillkiselev-slim)

