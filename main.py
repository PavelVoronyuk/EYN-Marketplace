from flask import Flask
from flask_restx import Api
from flask_jwt_extended import JWTManager
from products.app import products, ns_products
from users.app import users, ns_users
import uuid


app = Flask(__name__)
app.config["SECRET_KEY"] = "pencil_30000iq_gigabrain"
app.config["JWT_SECRET_KEY"] = "300iq_key"
app.register_blueprint(products)
app.register_blueprint(users)

api = Api(app)
api.add_namespace(ns_products)
api.add_namespace(ns_users)

jwt = JWTManager(app)

DEBUG = True
SECRET_KEY = uuid.uuid4()

if __name__ == "__main__":
    app.run(debug=True)
