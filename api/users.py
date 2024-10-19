# api/users.py
from flask import Blueprint, jsonify, request
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError
import bcrypt

# Configurações do MongoDB
MONGO_URI = "mongodb+srv://tccaplicativomanutencao:Aa194223@frotalizedb.oenoa.mongodb.net/?retryWrites=true&w=majority&appName=FrotalizeDB"
mongo_client = MongoClient(MONGO_URI)
db = mongo_client['frotalizeDB']  # Substitua pelo nome do seu banco de dados
users_collection = db['usuarios']  # Nome da coleção de usuários

users_api = Blueprint('users', __name__)

@users_api.route('/', methods=['GET'])
def get_users():
    """Retorna a lista de usuários."""
    users = list(users_collection.find({}, {'_id': 0}))  # Retorna todos os usuários sem o campo _id
    return jsonify(users), 200

@users_api.route('/', methods=['POST'])
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
        "cargo": data.get('cargo'),
        "departamento": data.get('departamento')
    }

    try:
        users_collection.insert_one(user)
        return jsonify(user), 201
    except DuplicateKeyError:
        return jsonify({"error": "Email já existe"}), 400

@users_api.route('/<email>', methods=['GET'])
def get_user(email):
    """Retorna um usuário específico."""
    user = users_collection.find_one({"email": email}, {'_id': 0})
    if user:
        return jsonify(user), 200
    return jsonify({"error": "Usuário não encontrado"}), 404

@users_api.route('/<email>', methods=['PUT'])
def update_user(email):
    """Atualiza os dados de um usuário específico."""
    data = request.get_json()
    if not data:
        return jsonify({"error": "Dados inválidos"}), 400

    update_fields = {k: v for k, v in data.items() if k != 'senha'}  # Não atualiza a senha diretamente
    if 'senha' in data:
        # Hash da nova senha
        update_fields['senha'] = bcrypt.hashpw(data['senha'].encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    result = users_collection.update_one({"email": email}, {"$set": update_fields})

    if result.modified_count == 0:
        return jsonify({"error": "Usuário não encontrado ou sem alterações"}), 404
    return jsonify({"message": "Usuário atualizado com sucesso"}), 200

@users_api.route('/<email>', methods=['DELETE'])
def delete_user(email):
    """Deleta um usuário específico."""
    result = users_collection.delete_one({"email": email})
    if result.deleted_count == 0:
        return jsonify({"error": "Usuário não encontrado"}), 404
    return jsonify({"message": "Usuário deletado com sucesso"}), 204
