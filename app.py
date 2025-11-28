from flask import Flask
from flask_cors import CORS
from database import db
from routes import bp
import pymysql
from dotenv import load_dotenv
import os
import cloudinary

load_dotenv()


def create_app():
    app = Flask(__name__)

    base_url = os.getenv("BASE_URL")

    if base_url:
        cors_origins = [
            base_url,
            "https://nego-maq.vercel.app",
            "http://localhost:5173",
            "http://localhost:9000",
        ]
    else:

        cors_origins = ["*"]

    CORS(
        app,
        resources={r"/*": {"origins": cors_origins}},
        supports_credentials=True,
        allow_headers=["Content-Type", "Authorization"],
        methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        max_age=3600,
    )

    DB_USER = os.getenv("DB_USER")
    DB_PASSWORD = os.getenv("DB_PASSWORD")
    DB_HOST = os.getenv("DB_HOST")
    DB_NAME = os.getenv("DB_NAME")
    DB_PORT = os.getenv("DB_PORT", "3306")

    DATABASE_URL = os.getenv("DATABASE_URL")
    if DATABASE_URL:
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URL
    else:
        app.config["SQLALCHEMY_DATABASE_URI"] = (
            f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
        )

    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")

    cloudinary.config(
        cloud_name=os.getenv("CLOUDE_NAME"),
        api_key=os.getenv("API_KEY"),
        api_secret=os.getenv("API_SECRET"),
        secure=True,
    )

    db.init_app(app)

    with app.app_context():
        db.create_all()

    app.register_blueprint(bp, url_prefix="/")

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
