auth/authz test app

Как запустить:

Вариант 1: быстро

bash:

- cd auth_test_app
- bash scripts/run.sh

Вариант 2: руками:)

bash:

- cd auth_test_app
- python3 -m venv .venv
- source .venv/bin/activate
- pip install -r requirements.txt
- uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload


Swagger:

- http://127.0.0.1:8000/docs


Тестовые пользователи:

- admin@example.com / Admin123!
- manager@example.com / Manager123!
- user@example.com / User12345!

!!!Возможные проблемы при запуске и их решения:

- Ошибка при установке зависимостей (pydantic-core / Rust)

Симптомы:

error: metadata-generation-failed
Cargo, the Rust package manager, is not installed

Причина:
Используется Python 3.14, для которого часть библиотек (например pydantic-core) не имеет готовых сборок.

Решение:
Использовать лучше Python 3.11 или 3.12.

py -3.12 -m venv .venv
source .venv/Scripts/activate
pip install -r requirements.txt
