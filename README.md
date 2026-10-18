# Клиент SampleAPIs Coffee

Небольшой Python-клиент для публичного SampleAPIs Coffee. Реализует CRUD: список, получение по id, создание, полная замена (PUT), частичное изменение (PATCH), удаление.
Выполнили:
Михин Матвей
Мамлеев Александр
Строгонов Игорь
Пухов Андрей

## Запуск

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python starter.py
```

Программа проходит полный сценарий: GET коллекции → POST → GET → PUT → GET → PATCH → GET → DELETE → GET (ожидается 404). Созданная запись удаляется в `finally`, даже если сценарий упал посередине.

