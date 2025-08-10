from flask import Blueprint
from routes.admin import admin_routes
from routes.public import public_routes
from routes.auth import auth_routes
from routes.events import event_routes


bp = Blueprint("main", __name__)

bp.register_blueprint(admin_routes)
bp.register_blueprint(public_routes)
bp.register_blueprint(auth_routes)
bp.register_blueprint(event_routes)
