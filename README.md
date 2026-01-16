# Интернет-магазин на Python + HTML (без Django)

Стек: **Flask + Jinja2 + SQLite (SQLAlchemy)**.

Реализовано:
- Главная страница с **регистрацией/авторизацией**
- Личный кабинет пользователя
- Личный кабинет администратора (CRUD товаров + заказы)
- Каталог, карточка товара, корзина, оформление заказа (демо)
- Адаптивная верстка под **720×1440** и десктопы **от 1200px**
- Для мобильной и десктопной версии используются **разные структуры блоков** (mobile-only / desktop-only)

---

## Быстрый старт (PyCharm / Windows / Linux)

### 1) Установка зависимостей
```bash
python -m venv venv
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

pip install -r requirements.txt
```

### 2) Инициализация БД и тестовые данные (ВАЖНО!)
**Вариант A (проще): через run.py**
```bash
python run.py init-db
python run.py seed
```

**Вариант B: через Flask CLI**
```bash
python -m flask --app run.py init-db
python -m flask --app run.py seed
```

Создастся:
- admin / admin123 (роль admin)
- user / user123 (роль user)
- несколько товаров

### 3) Запуск сервера
```bash
python run.py run
```

Откройте: http://127.0.0.1:5000

---

## Где заменить шрифт
Положите файл шрифта из задания в: `static/fonts/`  
и поправьте `static/css/styles.css` (блок `@font-face`).

---

## Страницы
- `/` главная (витрина + логин/регистрация)
- `/catalog` каталог
- `/product/<id>` товар
- `/cart` корзина
- `/checkout` оформление заказа (после входа)
- `/account` кабинет пользователя
- `/admin` кабинет администратора


✅ Корзина хранится в БД для авторизованных пользователей (сохраняется после выхода и между входами).


## Запуск (Windows)

1) Создайте виртуальное окружение:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2) Установите зависимости:

```powershell
python -m pip install -r requirements.txt
```

3) Создайте БД и демо-данные:

```powershell
python run.py init-db
python run.py seed
```

4) Запуск:

```powershell
python run.py
```

Админ: **admin / admin123**
Пользователь: **user / user123**
