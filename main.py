from flask import Flask
from flask_restx import Api
from flask_jwt_extended import JWTManager
from products.app import products, ns_products
from auth.app import auth, ns_auth
from extensions import limiter
import uuid


app = Flask(__name__)
app.config["SECRET_KEY"] = "pencil_30000iq_gigabrain"
app.config["JWT_SECRET_KEY"] = "300iq_key"
app.config["JWT_TOKEN_LOCATION"] = ["cookies"]  # Указываем, что JWT берётся из куков
app.config["JWT_COOKIE_CSRF_PROTECT"] = False

limiter.init_app(app)

app.register_blueprint(products)
app.register_blueprint(auth)

api = Api(app)
api.add_namespace(ns_products)
api.add_namespace(ns_auth)

jwt = JWTManager(app)




DEBUG = True
SECRET_KEY = uuid.uuid4()

if __name__ == "__main__":
    app.run(debug=True)
