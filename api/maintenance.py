# api/maintenance.py
from flask import Blueprint, jsonify, request
from pymongo import MongoClient

# Configurações do MongoDB
MONGO_URI = "mongodb+srv://tccaplicativomanutencao:Aa194223@frotalizedb.oenoa.mongodb.net/?retryWrites=true&w=majority&appName=FrotalizeDB"
mongo_client = MongoClient(MONGO_URI)
db = mongo_client['frotalizeDB']  # Substitua pelo nome do seu banco de dados
maintenance_collection = db['manutencoes']  # Nome da coleção de manutenções

maintenance_api = Blueprint('maintenance', __name__)

@maintenance_api.route('/', methods=['GET'])
def get_maintenance_records():
    """Retorna a lista de registros de manutenção."""
    records = list(maintenance_collection.find({}, {'_id': 0}))  # Retorna todos os registros sem o campo _id
    return jsonify(records), 200

@maintenance_api.route('/', methods=['POST'])
def create_maintenance_record():
    """Cria um novo registro de manutenção."""
    data = request.get_json()
    if not data or 'veiculo_id' not in data or 'descricao' not in data:
        return jsonify({"error": "Veículo ID e descrição são obrigatórios"}), 400

    record = {
        "veiculo_id": data['veiculo_id'],
        "descricao": data['descricao'],
        "data": data.get('data'),
        "status": data.get('status', 'Não Realizada')
    }

    maintenance_collection.insert_one(record)
    return jsonify(record), 201

@maintenance_api.route('/<int:record_id>', methods=['GET'])
def get_maintenance_record(record_id):
    """Retorna um registro de manutenção específico."""
    record = maintenance_collection.find_one({"_id": record_id}, {'_id': 0})
    if record:
        return jsonify(record), 200
    return jsonify({"error": "Registro de manutenção não encontrado"}), 404

@maintenance_api.route('/<int:record_id>', methods=['PUT'])
def update_maintenance_record(record_id):
    """Atualiza um registro de manutenção específico."""
    data = request.get_json()
    if not data:
        return jsonify({"error": "Dados inválidos"}), 400

    result = maintenance_collection.update_one({"_id": record_id}, {"$set": data})
    if result.modified_count == 0:
        return jsonify({"error": "Registro de manutenção não encontrado ou sem alterações"}), 404
    return jsonify({"message": "Registro de manutenção atualizado com sucesso"}), 200

@maintenance_api.route('/<int:record_id>', methods=['DELETE'])
def delete_maintenance_record(record_id):
    """Deleta um registro de manutenção específico."""
    result = maintenance_collection.delete_one({"_id": record_id})
    if result.deleted_count == 0:
        return jsonify({"error": "Registro de manutenção não encontrado"}), 404
    return jsonify({"message": "Registro de manutenção deletado com sucesso"}), 204
