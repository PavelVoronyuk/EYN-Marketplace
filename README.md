# 🛍️ Flask Product API

Flask-based RESTful API for user authentication and product management using JWT, Flask-RESTx, and SQLite/MySQL/Postgres.

## 🚀 Features

- 🔐 JWT-based authentication (with cookie support)
- 👤 User registration, login, logout, and profile
- 🛒 CRUD operations on products
- 📦 Token-based access control
- 📧 Optional email support with Flask-Mail
- 🔒 Rate-limiting support (Flask-Limiter)

## 🧱 Tech Stack

- Python 3.10+
- Flask
- Flask-RESTx
- Flask-JWT-Extended
- Flask-Mail
- SQLite / Peewee ORM (or your DB)
- dotenv (.env support)
- peewee
## 📦 Installation


git clone https://github.com/PavelVoronyuk/Marketplace-API.git
cd Marketplace-API
python -m venv venv
source venv/bin/activate  # On Windows: . Venv/Scripts/activate

pip install -r requirements.txt
