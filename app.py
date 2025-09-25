from flask import Flask
from database import db
from routes import bp
from flask_cors import CORS
import pymysql
from dotenv import load_dotenv
import os
import logging

# Importar as novas rotas
from routes.public.checkout import checkout_bp
from routes.public.webhooks import webhooks_bp

load_dotenv()

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/app.log'),
        logging.StreamHandler()
    ]
)

def create_app():
    app = Flask(__name__)
    
    # Configurar CORS
    CORS(app, origins=["http://localhost:9000"], 
         methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
         allow_headers=["Content-Type", "Authorization"])

    # Configurações do banco
    DB_USER = os.getenv("DATABASE_USER")
    DB_PASSWORD = os.getenv("DATABASE_PASSWORD")
    DB_HOST = os.getenv("DATABASE_HOST")
    DB_NAME = os.getenv("DATABASE_NAME")

    # Criar banco se não existir
    conn = pymysql.connect(host=DB_HOST, user=DB_USER, password=DB_PASSWORD)
    with conn.cursor() as cursor:
        cursor.execute(
            f"CREATE DATABASE IF NOT EXISTS {DB_NAME} CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci;"
        )
    conn.close()

    # Configurações da aplicação
    app.config["SQLALCHEMY_DATABASE_URI"] = (
        f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
    
    # Configurações para as integrações
    app.config["FRONTEND_URL"] = os.getenv("FRONTEND_URL", "http://localhost:9000")
    app.config["API_BASE_URL"] = os.getenv("API_BASE_URL", "http://localhost:5000")

    # Inicializar banco
    db.init_app(app)

    with app.app_context():
        db.create_all()

    # Registrar blueprints (rotas)
    app.register_blueprint(bp)  # Suas rotas existentes
    app.register_blueprint(checkout_bp)  # Novas rotas de checkout
    app.register_blueprint(webhooks_bp)  # Webhook do Mercado Pago
    
    # Rota de saúde
    @app.route('/health')
    def health_check():
        return {"status": "ok", "message": "API funcionando"}, 200

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)