# api/__init__.py
from flask import Blueprint

# Criação do Blueprint
api_bp = Blueprint('api', __name__)

# Importando as rotas
from .vehicles import vehicles_api
from .users import users_api
from .maintenance import maintenance_api
from .flow import flow_bp  

# Registrando as rotas
api_bp.register_blueprint(vehicles_api, url_prefix='/vehicles')
api_bp.register_blueprint(users_api, url_prefix='/users')
api_bp.register_blueprint(maintenance_api, url_prefix='/maintenance')
api_bp.register_blueprint(flow_bp, url_prefix='/flow')
