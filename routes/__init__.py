from flask import Blueprint
from routes.admin import admin_routes
from routes.pedidos_admin import admin_pedidos_routes
from routes.public import public_routes
from routes.pedidos_public import admin_pedidos_routes
from routes.auth import auth_routes
from routes.events import event_routes
from routes.enderecos_admin import admin_enderecos_routes
from routes.enderecos_public import public_enderecos_routes


bp = Blueprint("main", __name__)

bp.register_blueprint(admin_routes)
bp.register_blueprint(admin_pedidos_routes)
bp.register_blueprint(public_routes)
bp.register_blueprint(admin_pedidos_routes)
bp.register_blueprint(auth_routes)
bp.register_blueprint(event_routes)
bp.register_blueprint(admin_enderecos_routes)
bp.register_blueprint(public_enderecos_routes)
