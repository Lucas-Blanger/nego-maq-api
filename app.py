from flask import Flask
from config import SQLALCHEMY_DATABASE_URI, SQLALCHEMY_TRACK_MODIFICATIONS
from database import db
from routes import bp


def create_app():
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = SQLALCHEMY_DATABASE_URI
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = SQLALCHEMY_TRACK_MODIFICATIONS

    db.init_app(app)
    app.register_blueprint(bp)

    return app


app = create_app()

if __name__ == "__main__":
    app = create_app()
    try:
        with app.app_context():
            db.create_all()
        app.run(debug=True)
    except Exception as e:
        print("Erro ao iniciar o app:", e)
