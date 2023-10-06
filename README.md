# Учебный проект: Foodgram - продуктовый помощник
### Описание:
Foodgram это веб сервис, с помощью которого, пользователи смогут публиковать рецепты, подписываться на публикации других пользователей, добавлять понравившиеся рецепты в список «Избранное», а перед походом в магазин скачивать сводный список(в формате .txt) продуктов, необходимых для приготовления одного или нескольких выбранных блюд.

Вот, что было сделано в ходе работы над проектом:
* настроено взаимодействие Python-приложения с внешними API-сервисами;
* создан собственный API-сервис на базе проекта Django;
* создан Telegram-бот;
* подключено SPA к бэкенду на Django через API;
* созданы образы и запущены контейнеры Docker;
* созданы, развёрнуты и запущены на сервере мультиконтейнерные приложения;
* закреплены на практике основы DevOps, включая CI&CD.
### Используемые технологии:
![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![Django](https://img.shields.io/badge/django-%23092E20.svg?style=for-the-badge&logo=django&logoColor=white)
![DjangoREST](https://img.shields.io/badge/DJANGO-REST-ff1709?style=for-the-badge&logo=django&logoColor=white&color=ff1709&labelColor=gray)
![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=for-the-badge&logo=docker&logoColor=white)
![Nginx](https://img.shields.io/badge/nginx-%23009639.svg?style=for-the-badge&logo=nginx&logoColor=white)
![Postgres](https://img.shields.io/badge/postgres-%23316192.svg?style=for-the-badge&logo=postgresql&logoColor=white)
![GitHub Actions](https://img.shields.io/badge/github%20actions-%232671E5.svg?style=for-the-badge&logo=githubactions&logoColor=white)
### Как запустить проект:
#### API Foodgram локально:
1. Клонировать репозиторий и перейти в него в командной строке:
```
git clone git@github.com:Aleskerovz/foodgram-project-react.git
```
```
cd foodgram-project-react
```
2. Cоздать и активировать виртуальное окружение:
```
python3 -m venv venv
```
* Если у вас Linux/macOS
    ```
    source venv/bin/activate
    ```
* Если у вас windows
    ```
    source venv/scripts/activate
    ```
```
python3 -m pip install --upgrade pip
```
3. Установить зависимости из файла requirements.txt:
```
pip install -r requirements.txt
```
4. Перейти в дерикторию `backend/foodgram/settings.py` заменить настройки базы данных на SQLite:
```
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}
```

5. Перейти в дерикторию `backend` выполнить миграции и создать супер пользователя:
```
cd backend
```
```
python manage.py makemigrations
```
```
python manage.py migrate
```
```
python manage.py createsuperuser
```
6. Наполнить базу данных ингредиентами и тегами:
```
python manage.py load_ingredients
```
```
python manage.py load_tags
```
7. Запустить сервер разработки:
```
python manage.py runserver
```
### Подготовка сервера и деплой проекта:
1. В домашней директории сервера поочередно выполнить команды для установки **Docker** и **Docker Compose** для Linux.
```
sudo apt update
```
```
sudo apt install curl
```
```
curl -fSL https://get.docker.com -o get-docker.sh
```
```
sudo sh ./get-docker.sh
```
```
sudo apt-get install docker-compose-plugin 
```
2. Установить **Nginx** и настроить конфигурационный файл **default** так чтобы все запросы проксировались в контейнеры на порт **8000**
```
sudo apt install nginx -y 
```
```
sudo nano /etc/nginx/site-enabled/default
```
Создать примерно такую структуру:
```
server {
    server_name xxx.xxx.xx.xxx 
    xxxxxx.com;
    server_tokens off;

    location / {
      proxy_set_header Host $http_host;
      proxy_pass http://127.0.0.1:8000;
    }
}

```
Где `ххх.ххх.хх.ххх` - это IP вашего сервера.

А `хххххх.com` - домен ваiего сайта.

3. В домашней директории сервера создать папку `foodgram`.
4. В корне папки `foodgram` создать файл **.env** и заполнить его по шаблону.
```
POSTGRES_USER=<Логин для подключения к БД>
POSTGRES_PASSWORD=<Ваш пароль>
POSTGRES_DB=<Имя БД>
DB_HOST=<Имя контейнера БД>
DB_PORT=5432
SECRET_KEY=<50ти символьный ключ>
DEBUG=False
ALLOWED_HOSTS=<IP вашего сервера и домен сайта>
```
5. В репозиторие в разделе **Settings > Secrets and variables > Action** добавить следующие "секреты" по шаблону:
```
DOCKER_USERNAME <никнейм DockerHub>
DOCKER_PASSWORD <пароль от DockerHub>

HOST <IP вашего сервера>
SSH_KEY <Ваш приватный SSH-ключ>
SSH_PASSPHRASE <Ваш пароль от сервера>
USER <имя пользователя для подключения к серверу>

TELEGRAM_TO <id вашего телеграм аккаунта>
TELEGRAM_TOKEN <токен вашего телеграм бота>
``` 
6.Запустить workflow выполнив следующие команды:
```
git add .
```
```
git commit -m '<текст коммита>'
```
```
git push
```
Выполнив эти команды будет запущен тест, далее сбилдятся образы для бекенда, фронтенда, базы данных, и nginx и опубликуются в вашем аккаунте **DockerHub**. После этого будет выполнен автоматический деплой на ваш сервер. В конце в бот в месседжере **Телеграм** придёт уведомление об успешном деплое. 

### Автор проекта:
**Алескеров Заур**
<br>

<a href="https://t.me/aleskerov" target="_blank">
<img src=https://img.shields.io/badge/Telegram-2CA5E0?style=for-the-badge&logo=telegram&logoColor=white />
</a>