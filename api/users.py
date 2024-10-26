from flask import Blueprint, jsonify, request
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError
from bson import ObjectId
import bcrypt

# Configurações do MongoDB
MONGO_URI = "mongodb+srv://tccaplicativomanutencao:Aa194223@frotalizedb.oenoa.mongodb.net/?retryWrites=true&w=majority&appName=FrotalizeDB"
mongo_client = MongoClient(MONGO_URI)
db = mongo_client['frotalizeDB']
users_collection = db['usuarios']

users_api = Blueprint('users', __name__)

def serialize_user(user):
    """Converte um documento de usuário do MongoDB para um formato JSON serializável."""
    user['_id'] = str(user['_id'])  # Converte ObjectId para string
    return user

@users_api.route('/', methods=['GET'])
def get_users():
    """Retorna a lista de usuários."""
    try:
        users = list(users_collection.find())
        return jsonify([serialize_user(user) for user in users]), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@users_api.route('/new-user', methods=['POST'])
def create_user():
    """Cria um novo usuário."""
    data = request.get_json()
    if not data or 'nome' not in data or 'email' not in data or 'senha' not in data:
        return jsonify({"error": "Nome, email e senha são obrigatórios"}), 400

    # Hash da senha
    hashed_password = bcrypt.hashpw(data['senha'].encode('utf-8'), bcrypt.gensalt())

    user = {
        "nome": data['nome'],
        "email": data['email'],
        "senha": hashed_password.decode('utf-8'),
        "cpf": data.get('cpf')
    }

    try:
        users_collection.insert_one(user)
        return jsonify({"message": "Usuário criado com sucesso", "user": serialize_user(user)}), 201
    except DuplicateKeyError:
        return jsonify({"error": "Email já existe"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@users_api.route('/<email>', methods=['GET'])
def get_user(email):
    """Retorna um usuário específico."""
    try:
        user = users_collection.find_one({"email": email})
        if user:
            return jsonify(serialize_user(user)), 200
        return jsonify({"error": "Usuário não encontrado"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@users_api.route('/<email>', methods=['PUT'])
def update_user(email):
    """Atualiza os dados de um usuário específico."""
    data = request.get_json()
    if not data:
        return jsonify({"error": "Dados inválidos"}), 400

    update_fields = {k: v for k, v in data.items() if k != 'senha'}
    if 'senha' in data:
        update_fields['senha'] = bcrypt.hashpw(data['senha'].encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    try:
        result = users_collection.update_one({"email": email}, {"$set": update_fields})
        if result.modified_count == 0:
            return jsonify({"error": "Usuário não encontrado ou sem alterações"}), 404
        return jsonify({"message": "Usuário atualizado com sucesso"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@users_api.route('/<email>', methods=['DELETE'])
def delete_user(email):
    """Deleta um usuário específico."""
    try:
        result = users_collection.delete_one({"email": email})
        if result.deleted_count == 0:
            return jsonify({"error": "Usuário não encontrado"}), 404
        return jsonify({"message": "Usuário deletado com sucesso"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@users_api.route('/login', methods=['POST'])
def login_user():
    """Rota para login de usuário com email e senha."""
    data = request.get_json()
    if not data or 'email' not in data or 'senha' not in data:
        return jsonify({"error": "Email e senha são obrigatórios"}), 400

    user = users_collection.find_one({"email": data['email']})
    if user and bcrypt.checkpw(data['senha'].encode('utf-8'), user['senha'].encode('utf-8')):
        return jsonify({"message": "Login bem-sucedido", "user": serialize_user(user)}), 200
    else:
        return jsonify({"error": "Email ou senha inválidos"}), 401
