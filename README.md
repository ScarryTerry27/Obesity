# Obesity

Разработка системы на Python/Streamlit для ведения пациентов и расчёта медицинских шкал.

## Структура проекта

```
src/
├── main.py                # входная точка Streamlit‑приложения
├── backend/               # вспомогательные загрузчики данных
├── database/              # SQLAlchemy‑модели, сервисы и схемы Pydantic
└── frontend/              # страницы интерфейса и компоненты Streamlit

tests/                     # модульные тесты (pytest)
```

## Подготовка окружения

1. Установите зависимости и создайте виртуальное окружение:
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install streamlit sqlalchemy pandas pydantic pytest
   ```
2. Для работы с реальной базой данных можно поднять PostgreSQL из `src/docker-compose.yaml`:
   ```bash
   cd src
   docker compose up -d
   ```
   По умолчанию локальные функции используют SQLite (`patients_db.sqlite3`).

## Запуск приложения

Из корня репозитория выполните:
```bash
streamlit run src/main.py
```
Это откроет веб‑интерфейс, содержащий разделы пациентов, расчёт различных шкал
(ARISCAT, Caprini, El‑Ganzouri, Lee RCRI, STOP‑BANG и др.) и работу с «срезами» T0–T12.

## Тестирование

Для запуска автоматических тестов используйте:
```bash
pytest
```

## Содействие разработке

- Соблюдайте стиль PEP 8.
- Перед коммитом убеждайтесь, что все тесты проходят.
- Предложения и доработки оформляйте через pull‑request.

