# api/vehicles.py
from flask import Blueprint, jsonify, request
from pymongo import MongoClient

# Configurações do MongoDB
MONGO_URI = "mongodb+srv://tccaplicativomanutencao:Aa194223@frotalizedb.oenoa.mongodb.net/?retryWrites=true&w=majority&appName=FrotalizeDB"
mongo_client = MongoClient(MONGO_URI)
db = mongo_client['frotalizeDB']  # Substitua pelo nome do seu banco de dados
vehicles_collection = db['veiculos']  # Nome da coleção de veículos

vehicles_api = Blueprint('vehicles', __name__)

@vehicles_api.route('/', methods=['GET'])
def get_vehicles():
    """Retorna a lista de veículos."""
    vehicles = list(vehicles_collection.find({}, {'_id': 0}))  # Retorna todos os veículos sem o campo _id
    return jsonify(vehicles), 200

@vehicles_api.route('/', methods=['POST'])
def create_vehicle():
    """Cria um novo veículo."""
    data = request.get_json()
    if not data or 'modelo' not in data or 'placa' not in data:
        return jsonify({"error": "Modelo e placa são obrigatórios"}), 400

    vehicle = {
        "modelo": data['modelo'],
        "placa": data['placa'],
        "ano": data.get('ano'),
        "cor": data.get('cor'),
        "usuario_id": data.get('usuario_id')  # Adiciona o campo usuario_id se necessário
    }
    
    vehicles_collection.insert_one(vehicle)  # Insere o veículo na coleção
    return jsonify(vehicle), 201

@vehicles_api.route('/<int:vehicle_id>', methods=['GET'])
def get_vehicle(vehicle_id):
    """Retorna um veículo específico."""
    vehicle = vehicles_collection.find_one({"_id": vehicle_id}, {'_id': 0})
    if vehicle:
        return jsonify(vehicle), 200
    return jsonify({"error": "Veículo não encontrado"}), 404

@vehicles_api.route('/<int:vehicle_id>', methods=['PUT'])
def update_vehicle(vehicle_id):
    """Atualiza os dados de um veículo específico."""
    data = request.get_json()
    if not data:
        return jsonify({"error": "Dados inválidos"}), 400

    result = vehicles_collection.update_one({"_id": vehicle_id}, {"$set": data})
    if result.modified_count == 0:
        return jsonify({"error": "Veículo não encontrado ou sem alterações"}), 404

    return jsonify({"message": "Veículo atualizado com sucesso"}), 200

@vehicles_api.route('/<int:vehicle_id>', methods=['DELETE'])
def delete_vehicle(vehicle_id):
    """Deleta um veículo específico."""
    result = vehicles_collection.delete_one({"_id": vehicle_id})
    if result.deleted_count == 0:
        return jsonify({"error": "Veículo não encontrado"}), 404
    return jsonify({"message": "Veículo deletado com sucesso"}), 204
