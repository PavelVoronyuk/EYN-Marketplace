from flask import Blueprint
from flask_restx import Resource, Namespace
from flask_restx.reqparse import RequestParser
from werkzeug.security import generate_password_hash, check_password_hash
from models import Users

users = Blueprint("users", __name__)

ns_users = Namespace("users", description="Namsepace for users")


register_post = RequestParser()
register_post.add_argument("name", type=str, required=True, location="args")
register_post.add_argument("email", type=str, required=True, location="args")
register_post.add_argument("psw1", type=str, required=True, location="args")
register_post.add_argument("psw2", type=str, required=True, location="args")



@ns_users.route("/")
class Register(Resource):
    @ns_users.expect(register_post)
    def post(self):
        args = register_post.parse_args()
        if Users.select().where(Users.Email == args["email"]):
            return False, 400

        try:
            if args["psw1"] == args["psw2"]:
                Users.create(Username=args["name"],
                             Email=args["email"],
                             Password=generate_password_hash(args["psw1"]))
                return True, 200
            else:
                return "Passwords are not the same", 400
        except Exception as e:
            return e, 400
