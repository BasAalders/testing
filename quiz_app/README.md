# Quiz Application

This is a web application where users can create, play, and edit quizzes.

## Features

-   User registration, login, and logout.
-   Quiz creation with titles and descriptions.
-   Addition of multiple-choice questions to quizzes, with options and correct answer designation.
-   Quiz playing functionality with scoring and detailed results.
-   Editing of quiz details and questions by their creators.
-   Deletion of quizzes and questions by their creators.
-   Basic user interface styling.
-   Unit tests for core functionalities.

## Project Structure

```
quiz_app/
├── main/                 # Main Flask application package
│   ├── __init__.py       # Initializes Flask app, extensions, registers blueprints
│   ├── models.py         # SQLAlchemy database models
│   ├── forms.py          # WTForms definitions
│   ├── routes.py         # Application routes and view functions
│   └── ...
├── static/               # Static files (CSS, JavaScript, images)
│   ├── css/style.css
│   └── js/script.js
├── templates/            # HTML templates
│   ├── base.html
│   ├── login.html
│   └── ...
├── tests/                # Unit tests
│   ├── __init__.py
│   ├── base.py           # Base test case setup
│   ├── test_auth.py
│   └── test_quiz.py
├── venv/                 # Virtual environment (if created here)
├── database_schema.md    # Description of the database tables
├── requirements.txt      # Python package dependencies
├── run.py                # Script to run the Flask development server
└── test.sh               # Script to run unit tests
```

## Setup and Installation

1.  **Clone the repository (if applicable):**
    ```bash
    # git clone <repository-url>
    # cd quiz_app
    ```

2.  **Create and activate a virtual environment (recommended):**
    ```bash
    python -m venv venv
    ```
    *   On macOS and Linux:
        ```bash
        source venv/bin/activate
        ```
    *   On Windows:
        ```bash
        .\venv\Scripts\activate
        ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
    This will install Flask, Flask-SQLAlchemy, Flask-Login, Flask-WTF, Werkzeug, and other necessary packages. The application uses SQLite by default, so no external database server is needed for initial setup.

## Running the Application

1.  **Ensure your virtual environment is activated.**
2.  **Navigate to the `quiz_app` root directory (the one containing `run.py` and the `main` package):**
    ```bash
    cd path/to/your/quiz_app
    ```
3.  **Run the Flask development server:**
    ```bash
    python run.py
    ```
4.  Open your web browser and go to `http://127.0.0.1:5000/`.

The application will create a `site.db` SQLite database file in the `quiz_app` directory when it first runs (or in the instance folder, depending on specific SQLAlchemy configuration not detailed here but typical for Flask).

## Running Tests

1.  **Ensure your virtual environment is activated.**
2.  **Navigate to the `quiz_app` root directory (the one containing `run.py`, `test.sh` and the `main` package):**
    ```bash
    cd path/to/your/quiz_app
    ```
3.  **Execute the test script:**
    ```bash
    bash test.sh
    ```
    This will discover and run all unit tests located in the `tests/` directory.

## Technologies Used

-   Python
-   Flask (web framework)
-   Flask-SQLAlchemy (ORM)
-   Flask-Login (User session management)
-   Flask-WTF (Forms)
-   Werkzeug (Password hashing, WSGI utilities)
-   SQLite (Default database)
-   HTML / CSS
-   Jinja2 (Templating engine for Flask)
-   unittest (Python testing framework)

```
