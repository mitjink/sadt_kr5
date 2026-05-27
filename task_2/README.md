# Задание 2
1. Создать виртуальное окружение:
```bash
python -m venv .venv
```

2. Активировать виртуальное окружение:
## Windows
```bash
.venv\Scripts\activate
```

## macOS/Linux
```bash
source .venv/bin/activate
```

3. Установить зависимости:
```bash
pip install -r requirements.txt
```

4. Запустить приложение:
```bash
uvicorn app.main:app --reload
```

5. Запустить тесты:
```bash
pytest
```

6. Собрать и запустить контейнер:
```bash
docker compose up --build
```