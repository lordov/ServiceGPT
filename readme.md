# ServiceGPT

**ServiceGPT** — это веб-приложение для общения с нейросетью через API.
Можно подставить данные api и url любой нейросети и общаться с той неросетью с которой удобно будь-то GPT, Deepseek, Qwen и др.
Проект разработан на основе **FastAPI** для бэкенда и **React** с использованием **SCSS** для фронтенда. Каждый пользователь может зарегистрироваться, войти в аккаунт и вести свои чаты с AI, сохраняя историю сообщений.

---

## 🚀 Функционал

### 🔒 Аутентификация:
- Регистрация нового пользователя.
- Вход в аккаунт через JWT-токены.
- Выход из системы.

### 💬 Чаты с ИИ:
- Отправка сообщений нейросети через OpenAI API.
- Автоматическое создание чата при первом сообщении.
- Сохранение истории сообщений для каждого пользователя.
- Поддержка разметки текста и подсветка синтаксиса для кода.
- Возможность копировать фрагменты кода из сообщений.

---

## 🛠️ Технологии

### Backend:
- **FastAPI** — Веб-фреймворк.
- **SQLAlchemy** — Работа с базой данных.
- **aiomysql** — Асинхронное подключение к MySQL.
- **JWT** — Аутентификация.
- **Alembic** — Миграции БД.

### Frontend:
- **React** — Основной фреймворк.
- **SCSS** — Стилизация интерфейса.
- **Axios** — Для выполнения HTTP-запросов.
- **React Router** — Навигация.
- **Framer Motion** — Анимации.

### API:
- Подключение к **OpenAI API** для генерации ответов.

### Tools:
- **Docker** — Контейнеризация приложения.
---

## 📦 Установка проекта

### 🔗 Клонирование репозитория
```bash
git clone https://github.com/your-username/servicegpt.git
cd servicegpt

⚙️ Настройка переменных окружения
Создайте файл .env в корне проекта и укажите следующие переменные:


DB_USER=root
DB_PASSWORD=10101010
DB_HOST=localhost
DB_NAME=chatgpt_db

GPT_API_KEY=api-key
GPT_URL=url

📌 Установка зависимостей
cd backend
python -m venv venv
source venv/bin/activate  # Для Windows: venv\Scripts\activate
pip install -r requirements.txt

Frontend:
cd frontend
npm install

cd backend
alembic upgrade head

🏃 Запуск проекта
Запуск бэкенда:
cd backend
uvicorn main:app --reload


Запуск фронтенда:
cd frontend
npm start

servicegpt/
│
├── backend/
│   ├── app/
│   │   ├── main.py         # Точка входа в приложение
│   │   ├── models/         # SQLAlchemy модели
│   │   ├── routes/         # Эндпоинты FastAPI
│   │   ├── schemas/        # Pydantic схемы
│   │   ├── services/       # Логика бизнес-процессов
│   │   └── utils/          # Вспомогательные функции
│   ├── alembic/            # Миграции базы данных
│   └── requirements.txt    # Зависимости Python
│
├── frontend/
│   ├── src/
│   │   ├── components/     # Компоненты интерфейса
│   │   ├── pages/          # Страницы приложения (Chat, Login, Register)
│   │   ├── styles/         # SCSS стили
│   │   ├── App.jsx         # Основной компонент
│   │   └── index.js        # Точка входа React
│   └── package.json        # Зависимости проекта
│
└── README.md
