from flask import Blueprint
from routes.admin.admin import admin_routes
from routes.admin.pedidos_admin import admin_pedidos_routes
from routes.public import public_routes
from routes.public.pedidos_public import public_routes_pedidos
from routes.public.auth import auth_routes
from routes.public.enderecos_public import public_enderecos_routes
from routes.public.melhor_envio import frete_routes
from routes.public.pagamento import pagamentos_routes

bp = Blueprint("main", __name__)

bp.register_blueprint(admin_routes)
bp.register_blueprint(admin_pedidos_routes)
bp.register_blueprint(public_routes)
bp.register_blueprint(public_routes_pedidos)
bp.register_blueprint(auth_routes)
bp.register_blueprint(public_enderecos_routes)
bp.register_blueprint(frete_routes)
bp.register_blueprint(pagamentos_routes)
