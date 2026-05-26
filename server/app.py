from flask import Flask, request, session, jsonify
from flask_restful import Api, Resource
from flask_cors import CORS

from config import Config, db, migrate, bcrypt
from models import User, Recipe


app = Flask(__name__)

app.config.from_object(Config)

CORS(app, supports_credentials=True)

db.init_app(app)
migrate.init_app(app, db)
bcrypt.init_app(app)

api = Api(app)


# ---------------- SIGNUP ---------------- #

class Signup(Resource):

    def post(self):

        data = request.get_json()

        try:
            user = User(
                username=data["username"],
                image_url=data.get("image_url"),
                bio=data.get("bio")
            )

            user.password_hash = data["password"]

            db.session.add(user)
            db.session.commit()

            session["user_id"] = user.id

            return user.to_dict(
                only=("id", "username", "image_url", "bio")
            ), 201

        except Exception as e:
            db.session.rollback()

            return {
                "errors": [str(e)]
            }, 422


# ---------------- CHECK SESSION ---------------- #

class CheckSession(Resource):

    def get(self):

        user_id = session.get("user_id")

        if user_id:

            user = User.query.get(user_id)

            if user:
                return user.to_dict(
                    only=("id", "username", "image_url", "bio")
                ), 200

        return {
            "error": "Unauthorized"
        }, 401


# ---------------- LOGIN ---------------- #

class Login(Resource):

    def post(self):

        data = request.get_json()

        username = data.get("username")
        password = data.get("password")

        user = User.query.filter(
            User.username == username
        ).first()

        if user and user.authenticate(password):

            session["user_id"] = user.id

            return user.to_dict(
                only=("id", "username", "image_url", "bio")
            ), 200

        return {
            "error": "Invalid username or password"
        }, 401


# ---------------- LOGOUT ---------------- #

class Logout(Resource):

    def delete(self):

        if session.get("user_id"):

            session.pop("user_id")

            return {}, 204

        return {
            "error": "Unauthorized"
        }, 401


# ---------------- RECIPES ---------------- #

class RecipeIndex(Resource):

    def get(self):

        if not session.get("user_id"):

            return {
                "error": "Unauthorized"
            }, 401

        recipes = Recipe.query.all()

        return [
            recipe.to_dict(
                only=(
                    "id",
                    "title",
                    "instructions",
                    "minutes_to_complete",
                    "user.id",
                    "user.username",
                    "user.image_url",
                    "user.bio"
                )
            )
            for recipe in recipes
        ], 200

    def post(self):

        user_id = session.get("user_id")

        if not user_id:

            return {
                "error": "Unauthorized"
            }, 401

        data = request.get_json()

        try:

            recipe = Recipe(
                title=data["title"],
                instructions=data["instructions"],
                minutes_to_complete=data["minutes_to_complete"],
                user_id=user_id
            )

            db.session.add(recipe)
            db.session.commit()

            return recipe.to_dict(
                only=(
                    "id",
                    "title",
                    "instructions",
                    "minutes_to_complete",
                    "user.id",
                    "user.username",
                    "user.image_url",
                    "user.bio"
                )
            ), 201

        except Exception as e:

            db.session.rollback()

            return {
                "errors": [str(e)]
            }, 422


# ---------------- ROUTES ---------------- #

api.add_resource(Signup, "/signup")
api.add_resource(CheckSession, "/check_session")
api.add_resource(Login, "/login")
api.add_resource(Logout, "/logout")
api.add_resource(RecipeIndex, "/recipes")


if __name__ == "__main__":
    app.run(port=5555, debug=True)