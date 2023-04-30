# BURNSCOPE

BURNSCOPE - это телеграм-бот, который поможет вам быстро найти интересующие товары по низким ценам. Введите ссылку на товар с определенных сайтов или просто напишите название товара боту, и вы получите результат. Основные функции включают сохранение списка товаров, ежедневные уведомления об изменении цены, сравнение цен на разных маркетплейсах и отслеживание цены товара.

## Технологии

- Python
- Selenium

## Установка

Для работы проекта вам понадобится настроить `config.cfg`, создать базу данных PostgreSQL, а также установить webdriver и добавить его в PATH.

### Настройка config.cfg

Откройте файл `config.cfg` и внесите следующие изменения:

1. Укажите ваш Telegram API token
2. Укажите настройки подключения к вашей базе данных PostgreSQL
3. Укажите другие настройки, если это необходимо

### Создание базы данных PostgreSQL

Создайте новую базу данных PostgreSQL и выполните следующие шаги:

1. Создайте таблицы, используя SQL-скрипты из файла `init`
2. Настройте подключение к базе данных в файле `config.cfg`

### Установка webdriver

Для работы с Selenium вам потребуется установить соответствующий webdriver. Выберите webdriver для вашего браузера и следуйте инструкциям по установке:

- [Chrome](https://sites.google.com/a/chromium.org/chromedriver/downloads)
- [Firefox](https://github.com/mozilla/geckodriver/releases)
- [Safari](https://webkit.org/blog/6900/webdriver-support-in-safari-10/)

После установки webdriver, добавьте его в переменную среды PATH.

## Запуск

Чтобы запустить BURNSCOPE, выполните следующую команду:

```
python base_bot.py
```
