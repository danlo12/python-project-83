### Hexlet tests and linter status:
[![Actions Status](https://github.com/danlo12/python-project-83/actions/workflows/hexlet-check.yml/badge.svg)](https://github.com/danlo12/python-project-83/actions)

# Page Analyzer

## Description

**Page Analyzer** is a web application that analyzes specified pages for SEO-friendliness. The project is developed using the Flask framework and provides an interface for entering URLs, sending network requests, and storing data in a database. The web application analyzes pages, extracts metadata, and saves the results in a database for further analysis.

The project includes:
- Core principles of working with routing, request handlers, and templating based on the MVC architecture.
- Interactive pages using Bootstrap templates and styles.
- Database interaction using the psycopg2 library.
- CI/CD setup and deployment on the Render.com hosting platform.

## Objectives

The project aims to develop the following skills:
- Basics of web development with Python using Flask.
- Working with the HTTP protocol and client-server architecture.
- Designing a database and executing SQL queries.
- Using Bootstrap for interface styling.
- Setting up automated deployment on a PaaS platform.

## Tools Used

- **Flask**: A lightweight web framework for creating web applications in Python.
- **Jinja2**: A templating engine used to generate HTML pages on the server.
- **psycopg2**: A library for interacting with PostgreSQL databases via Python.
- **Bootstrap**: A CSS framework for styling and creating responsive designs.
- **Gunicorn**: A WSGI HTTP server for deploying the application in production.
- **Render.com**: A PaaS platform for automated deployment and hosting of web applications.
- **GitHub Actions**: A CI/CD platform for automated testing and deployment of the application.

## Installation and Setup

1. Clone the repository:
    ```bash
    git clone https://github.com/your-username/page-analyzer.git
    ```

2. Navigate to the project directory:
    ```bash
    cd page-analyzer
    ```

3. Create a virtual environment and activate it:
    ```bash
    python -m venv venv
    source venv/bin/activate  # For Windows: venv\Scripts\activate
    ```

4. Install the dependencies:
    ```bash
    pip install -r requirements.txt
    ```

5. Set up environment variables for database connection. Create a `.env` file in the project root and add the following line:
    ```
    DATABASE_URL=your_database_url
    ```

6. Run the application:
    ```bash
    flask run
    ```

7. Open your browser and go to [http://127.0.0.1:5000](http://127.0.0.1:5000) to view the application.

## Описание

**Page Analyzer** – это веб-приложение, которое анализирует указанные страницы на SEO-пригодность. Проект разработан с использованием фреймворка Flask и предоставляет интерфейс для ввода URL-адресов, отправки запросов по сети и сохранения данных в базе данных. Веб-приложение анализирует страницы, извлекает метаданные и сохраняет результаты в базе данных для дальнейшего анализа.

Проект включает в себя:
- Основные принципы работы с роутингом, обработчиками запросов и шаблонизатором на основе MVC-архитектуры.
- Интерактивные страницы с использованием шаблонов и стилей Bootstrap.
- Взаимодействие с базой данных с помощью библиотеки psycopg2.
- Настройка CI/CD и деплой на хостинг платформе Render.com.

## Цель

Проект нацелен на отработку следующих навыков:
- Основы веб-разработки на Python с использованием Flask.
- Работа с HTTP-протоколом и клиент-серверной архитектурой.
- Проектирование базы данных и выполнение SQL-запросов.
- Использование Bootstrap для стилизации интерфейса.
- Настройка автоматизированного деплоя на платформе PaaS.

## Используемые инструменты

- **Flask**: Легковесный веб-фреймворк для создания веб-приложений на Python.
- **Jinja2**: Шаблонизатор, используемый для генерации HTML страниц на сервере.
- **psycopg2**: Библиотека для взаимодействия с PostgreSQL базой данных через Python.
- **Bootstrap**: CSS-фреймворк для стилизации и создания адаптивного дизайна.
- **Gunicorn**: WSGI HTTP сервер для развертывания приложения в продакшене.
- **Render.com**: PaaS платформа для автоматизированного деплоя и хостинга веб-приложений.
- **GitHub Actions**: CI/CD платформа для автоматизированного тестирования и деплоя приложения.

## Установка и запуск

1. Клонируйте репозиторий:
    ```bash
    git clone https://github.com/your-username/page-analyzer.git
    ```

2. Перейдите в директорию проекта:
    ```bash
    cd page-analyzer
    ```

3. Создайте виртуальное окружение и активируйте его:
    ```bash
    python -m venv venv
    source venv/bin/activate  # Для Windows: venv\Scripts\activate
    ```

4. Установите зависимости:
    ```bash
    pip install -r requirements.txt
    ```

5. Настройте переменные окружения для подключения к базе данных. Создайте файл `.env` в корне проекта и добавьте следующую строку:
    ```
    DATABASE_URL=your_database_url
    ```

6. Запустите приложение:
    ```bash
    flask run
    ```

7. Откройте браузер и перейдите по адресу [http://127.0.0.1:5000](http://127.0.0.1:5000), чтобы увидеть приложение.