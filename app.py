from flask import Flask
from database import db
from routes import bp
from flask_cors import CORS
import pymysql
from dotenv import load_dotenv
import os
import cloudinary

load_dotenv()


def create_app():
    app = Flask(__name__)
    CORS(app, origins=["http://localhost:9000"])

    DB_USER = os.getenv("DATABASE_USER")
    DB_PASSWORD = os.getenv("DATABASE_PASSWORD")
    DB_HOST = os.getenv("DATABASE_HOST")
    DB_NAME = os.getenv("DATABASE_NAME")

    conn = pymysql.connect(host=DB_HOST, user=DB_USER, password=DB_PASSWORD)
    with conn.cursor() as cursor:
        cursor.execute(
            f"CREATE DATABASE IF NOT EXISTS {DB_NAME} CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci;"
        )
    conn.close()

    app.config["SQLALCHEMY_DATABASE_URI"] = (
        f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"
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

    app.register_blueprint(bp)
    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
