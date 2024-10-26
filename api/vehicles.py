from flask import Blueprint, jsonify, request
from pymongo import MongoClient
from bson import ObjectId

# Configurações do MongoDB
MONGO_URI = "mongodb+srv://tccaplicativomanutencao:Aa194223@frotalizedb.oenoa.mongodb.net/?retryWrites=true&w=majority&appName=FrotalizeDB"
mongo_client = MongoClient(MONGO_URI)
db = mongo_client['frotalizeDB']  # Nome do seu banco de dados
vehicles_collection = db['veiculos']  # Nome da coleção de veículos
users_collection = db['usuarios']  # Nome da coleção de usuários

vehicles_api = Blueprint('vehicles', __name__)

def is_valid_user(user_id):
    """Verifica se um usuário existe com o ID fornecido."""
    return users_collection.find_one({"_id": ObjectId(user_id)}) is not None

def serialize_vehicle(vehicle):
    """Converte um documento de veículo do MongoDB para um formato JSON serializável."""
    vehicle['_id'] = str(vehicle['_id'])  # Converte ObjectId para string
    vehicle['usuario_id'] = str(vehicle['usuario_id'])  # Converte ObjectId para string
    return vehicle

@vehicles_api.route('/', methods=['GET'])
def get_vehicles():
    """Retorna a lista de veículos."""
    vehicles = list(vehicles_collection.find())
    return jsonify([serialize_vehicle(vehicle) for vehicle in vehicles]), 200  # Serializa cada veículo

@vehicles_api.route('/', methods=['POST'])
def create_vehicle():
    """Cria um novo veículo."""
    data = request.get_json()
    if not data or 'modelo' not in data or 'placa' not in data or 'usuario_id' not in data:
        return jsonify({"error": "Modelo, placa e usuario_id são obrigatórios"}), 400

    if not is_valid_user(data['usuario_id']):
        return jsonify({"error": "Usuário não encontrado"}), 404

    vehicle = {
        "modelo": data['modelo'],
        "placa": data['placa'],
        "ano": data.get('ano'),
        "cor": data.get('cor'),
        "km_rodado": data.get('km_rodado'),

        "usuario_id": ObjectId(data['usuario_id'])  # Converte para ObjectId
    }
    
    vehicles_collection.insert_one(vehicle)  # Insere o veículo na coleção
    return jsonify(serialize_vehicle(vehicle)), 201  # Serializa o veículo criado

@vehicles_api.route('/<vehicle_id>', methods=['GET'])
def get_vehicle(vehicle_id):
    """Retorna um veículo específico."""
    vehicle = vehicles_collection.find_one({"_id": ObjectId(vehicle_id)})
    if vehicle:
        return jsonify(serialize_vehicle(vehicle)), 200  # Serializa o veículo
    return jsonify({"error": "Veículo não encontrado"}), 404

@vehicles_api.route('/<vehicle_id>', methods=['PUT'])
def update_vehicle(vehicle_id):
    """Atualiza os dados de um veículo específico."""
    data = request.get_json()
    if not data:
        return jsonify({"error": "Dados inválidos"}), 400

    if 'usuario_id' in data and not is_valid_user(data['usuario_id']):
        return jsonify({"error": "Usuário não encontrado"}), 404

    result = vehicles_collection.update_one({"_id": ObjectId(vehicle_id)}, {"$set": data})
    if result.modified_count == 0:
        return jsonify({"error": "Veículo não encontrado ou sem alterações"}), 404

    return jsonify({"message": "Veículo atualizado com sucesso"}), 200

@vehicles_api.route('/<vehicle_id>', methods=['DELETE'])
def delete_vehicle(vehicle_id):
    """Deleta um veículo específico."""
    result = vehicles_collection.delete_one({"_id": ObjectId(vehicle_id)})
    if result.deleted_count == 0:
        return jsonify({"error": "Veículo não encontrado"}), 404
    return jsonify({"message": "Veículo deletado com sucesso"}), 204


@vehicles_api.route('/by-user-id/<usuario_id>', methods=['GET'])
def get_vehicles_by_user_id(usuario_id):
    """Retorna a lista de veículos de um usuário específico."""
    
    try:
        # Converte o `usuario_id` para `ObjectId`
        usuario_id = ObjectId(usuario_id)
    except:
        return jsonify({"error": "ID do usuário inválido"}), 400
    
    # Filtra os veículos pelo `usuario_id`
    vehicles = list(vehicles_collection.find({"usuario_id": usuario_id}))
    
    # Serializa cada veículo para retornar na resposta JSON
    return jsonify([serialize_vehicle(vehicle) for vehicle in vehicles]), 200
