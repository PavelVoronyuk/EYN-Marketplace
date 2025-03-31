from flask import Blueprint, make_response, request
from flask_restx import Resource, Namespace, fields
from flask_restx.reqparse import RequestParser
from flask_jwt_extended import (create_access_token, create_refresh_token, get_jwt_identity,
                                 jwt_required, set_access_cookies, unset_jwt_cookies,
                                 set_refresh_cookies)
from werkzeug.security import generate_password_hash, check_password_hash
from models import Users


auth = Blueprint("auth", __name__)

ns_auth = Namespace("auth", description="Namsepace for auth")



register_post = RequestParser()
register_post.add_argument("name", type=str, required=True, location="args")
register_post.add_argument("email", type=str, required=True, location="args")
register_post.add_argument("psw1", type=str, required=True, location="args")
register_post.add_argument("psw2", type=str, required=True, location="args")

login_post = RequestParser()
login_post.add_argument("email", type=str, required=True, location="args")
login_post.add_argument("psw", type=str, required=True, location="args")

get_profile_model = ns_auth.model("user", {
    "name": fields.String(attribute="Username"),
    "email": fields.String(attribute="Email")
})


@ns_auth.route("/register")
class Register(Resource):
    @ns_auth.expect(register_post)
    def post(self):
        args = register_post.parse_args()


        try:
            if Users.get_or_none(Users.Email == args["email"]) is not None:
                return "User already exists!", 400
            if args["psw1"] == args["psw2"]:
                Users.create(Username=args["name"],
                             Email=args["email"],
                             Password=generate_password_hash(args["psw1"]))
                return "Success", 200
            else:
                return "Passwords are not the same", 400
        except Exception as e:
            return str(e), 400

@ns_auth.route("/login")
class Login(Resource):
    @ns_auth.expect(login_post)
    @jwt_required(optional=True, locations=["cookies"])
    @limiter.limit("5 per minute")
    def post(self):
        args = login_post.parse_args()

        if get_jwt_identity():
            return "Already logged in!", 400

        user:Users
        try:
            user = Users.get_or_none(Users.Email==args["email"])
            if user is not None:
                if check_password_hash(user.Password, args["psw"]):
                    access_token = create_access_token(identity=args["email"])
                    refresh_token = create_refresh_token(identity=args["email"])
                    # csrf_token = get_csrf_token(encoded_token=access_token)
                    response = make_response({"msg": "Login successful"}, 200)
                    set_access_cookies(response, access_token, max_age=1800)
                    set_refresh_cookies(response, refresh_token)
                    # response.set_cookie("csrf_access_token", csrf_token, httponly=False)
                    return response
                else:
                    return "Invalid password", 400
            else:
                return "User Not Found", 400

        except Exception as e:
            return str(e), 400

@ns_auth.route("/profile")
class Profile(Resource):
    @jwt_required()
    @ns_auth.marshal_with(get_profile_model)
    def get(self):

        try:
            user: Users
            email = get_jwt_identity()
            user = Users.get_or_none(Users.Email==email)
            return user
        except Exception as e:
            return str(e), 400


@ns_auth.route("/logout")
class Logout(Resource):
    @jwt_required(optional=True)
    def post(self):
        if get_jwt_identity():
            try:
                response = make_response("Logged out successfully", 200)
                unset_jwt_cookies(response)
                return response
            except Exception as e:
                return str(e), 400
        else:
            return "Already logged out!", 400

@ns_auth.route("/refresh")
class Refresh(Resource):
    @jwt_required(refresh=True)
    def post(self):
        new_access_token = create_access_token(identity=get_jwt_identity())
        response = make_response("Token refreshed", 200)
        set_access_cookies(response, new_access_token)
        return response