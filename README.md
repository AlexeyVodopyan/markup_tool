# Markup Tool

*Markup Tool* - приложение для классификации картинок.

Приложение состоит из 2 частей:

- Telegram-bot для разметки изображений
- Веб-админка для управления задачами и просмотра статистики


## Getting started

* Демо-работы telegram-бота: https://t.me/markup_tool_bot
* Демо-работы веб-админки:

## Особенности

- После регистрации пользователю автоматически назначаются все новые задачи.
Аналогично и старому пользователю, если он давно не заходил, при входе назначатся задачи, которые он еще не выполнял

## Будущие улучшения

- Выдавать картинки, которые еще не размечали
- Развернуть хранилище фотографий
- Сделать статистику по задачам
- Добавить визуализацию статистики в админке
- Прикрутить Redis, чтобы промежуточное состояние в боте не сбрасывалось
- Расширить функционал админки под назначение пользователей на задачи
- Объединить часть запросов


## Инструкция по развертыванию приложения

### Предварительная подготовка:

Для запуска понадобится:

- установленный docker. Его можно скачать [с официального сайта](https://www.docker.com/)
- telegram-бот. Его нужно создать через менеджер ботов BotFather [по ссылке](https://telegram.me/BotFather).
Для работы приложения понадобится токен бота
- настроить переменные окружения. Пример необходимых переменных дан в файле [.env.evample](.env.example)
- объявить публичные порты у контейнера c веб-админкой (и у других если вам понадобится).
Для этого можно создать файл docker-compose.override.yml в корне проекта


### Пошаговая инструкция после предварительной подготовки:

1) Запускаем контейнеры командой в терминале из корня проекта:
`docker compose up`
2) Необходимо накатить миграции на БД. Для этого заходим в терминал контейнера с веб-админкой, в терминале хоста:
`docker exec -it web_admin bash`
3) Накатываем миграции: `alembic upgrade head`
4) Нужно сгенерировать администратора в базе: для этого можно запустить скрипт в: `src/admin_panel/add_new_admins.py`
5) Выходим из терминала контейнера сочетанием клавиш `Ctrl + D`
6) Теперь админка доступна по адресу: `http://localhost:ваш_порт`, по умолчанию по адресу `http://localhost:8000/`
7) В окне логина и пароля вводим сгенерированные данные и попадаем на форму
