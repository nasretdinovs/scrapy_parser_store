# Парсер данных о товарах
Парсинг данных о продукции с интернет-магазина

## Установка

Создайте и активируйте виртуальное окружение:

В Linux
```bash
python3 -m venv venv
source venv/bin/activate
```

В Windows
```bash
python -m venv venv
source venv/Scripts/activate
```

Используйте [pip](https://pip.pypa.io/en/stable/)
для установки зависимостей.

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

## Запуск
Команда для запуска:
```
scrapy crawl store
```
Результаты парсинга появятся в папке **data** в формате JSON
