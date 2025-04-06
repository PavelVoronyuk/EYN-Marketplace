from flask import Flask
from flask_restx import Api
from flask_jwt_extended import JWTManager
from products.app import products, ns_products
from auth.app import auth, ns_auth
from extensions import limiter, mail
import uuid
from flask_mail import Mail
from dotenv import load_dotenv
from os import getenv
#
load_dotenv()

app = Flask(__name__)
app.config["SECRET_KEY"] = getenv("SECRET_KEY")
app.config["JWT_SECRET_KEY"] = getenv("JWT_SECRET_KEY")
app.config["JWT_TOKEN_LOCATION"] = ["cookies"]  # Указываем, что JWT берётся из куков
app.config["JWT_COOKIE_CSRF_PROTECT"] = False

app.config['MAIL_SERVER'] = 'smtp.gmail.com'  # или smtp.yandex.ru, smtp.mail.ru
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = getenv("MAIL_USERNAME")
app.config['MAIL_PASSWORD'] = getenv("MAIL_PASSWORD")
app.config['MAIL_DEFAULT_SENDER'] = getenv("MAIL_DEFAULT_SENDER")

limiter.init_app(app)
mail.init_app(app)

app.register_blueprint(products)
app.register_blueprint(auth)

api = Api(app)
api.add_namespace(ns_products)
api.add_namespace(ns_auth)

jwt = JWTManager(app)


if __name__ == "__main__":
    app.run(debug=True)
