from flask import Blueprint, make_response, request, url_for
from flask_restx import Resource, Namespace, fields
from flask_restx.reqparse import RequestParser
from flask_jwt_extended import (create_access_token, create_refresh_token, get_jwt_identity,
                                 jwt_required, set_access_cookies, unset_jwt_cookies,
                                 set_refresh_cookies)
from werkzeug.security import generate_password_hash, check_password_hash
from models import Users
from extensions import limiter, mail
import secrets
from flask_mail import Message
from datetime import datetime, timedelta


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

delete_acc = RequestParser()
delete_acc.add_argument("psw", type=str, required=True, location="args")

admin_delete_acc = RequestParser()
admin_delete_acc.add_argument("user_id", type=int, required=True, location="args")

post_forgot_psw = RequestParser()
post_forgot_psw.add_argument("email", type=str, required=True, location="args")

post_reset_psw = RequestParser()
post_reset_psw.add_argument("psw", type=str, required=True, location="args")


get_profile_model = ns_auth.model("user", {
    "name": fields.String(attribute="Username"),
    "email": fields.String(attribute="Email")
})


@ns_auth.route("/register")
class Register(Resource):
    @jwt_required(optional=True)
    @ns_auth.expect(register_post)
    def post(self):
        args = register_post.parse_args()

        if get_jwt_identity():
            return "Already logged in!", 400

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
    @jwt_required(optional=True)
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

@ns_auth.route("/delete-account")
class DelAccount(Resource):
    @jwt_required()
    @ns_auth.expect(delete_acc)
    def delete(self):
        args = delete_acc.parse_args()
        psw = args["psw"]

        user: Users
        user = Users.get_or_none(Users.Email == get_jwt_identity())
        try:
            if check_password_hash(user.Password, psw):
                response = make_response("Success", 200)
                unset_jwt_cookies(response)
                user.delete_instance()
                return response
            else:
                return "Wrong password!", 400
        except Exception as e:
            return str(e), 400

@ns_auth.route("/admin-delete-account")
class AdminDelAccount(Resource):
    @jwt_required()
    @ns_auth.expect(admin_delete_acc)
    def delete(self):
        args = admin_delete_acc.parse_args()
        user_id = args["user_id"]

        admin: Users
        admin = Users.get_or_none(Users.Email == get_jwt_identity())
        try:
            if admin.Role.lower() == "admin":
                user = Users.get_or_none(Users.UserId == user_id)
                user.delete_instance()
                response = make_response("Success", 200)
                unset_jwt_cookies(response)
                return response
            else:
                return "You can't do that.", 400
        except Exception as e:
            return str(e), 400

@ns_auth.route("/forgot-password")
class ForgotPassword(Resource):
    @ns_auth.expect(post_forgot_psw)
    def post(self):
        email = post_forgot_psw.parse_args()["email"]
        user: Users = Users.get_or_none(Users.Email == email)

        if not user:
            return "User not found", 400
        try:
            reset_token = secrets.token_urlsafe(32)
            user.Reset_token = reset_token
            user.Reset_token_expiry = datetime.now() + timedelta(hours=1)
            user.save()

            reset_url = url_for("auth_reset_password", token=reset_token, _external=True)
            msg = Message("Password reset", sender="workprofi33@gmail.com", recipients=[email],
                        body=f"Click here to reset your password: {reset_url}")
            mail.send(msg)

            return "Password reset email sent.", 200
        except Exception as e:
            return str(e), 400

@ns_auth.route("/reset-password/<string:token>")
class ResetPassword(Resource):
    @ns_auth.expect(post_reset_psw)
    def post(self, token):
        user: Users = Users.get_or_none(Users.Reset_token == token)
        if not user or user.Reset_token_expiry < datetime.now():
            return "Invalid or expired token.", 400

        try:
            new_psw = post_reset_psw.parse_args()["psw"]
            user.Password = generate_password_hash(new_psw)
            user.Reset_token = None
            user.Reset_token_expiry = None
            user.save()

            return "Successfully changed password.", 200
        except Exception as e:
            return str(e), 400