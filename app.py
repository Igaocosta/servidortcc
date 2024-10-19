# app.py
from flask import Flask, jsonify
from flask_cors import CORS
from pymongo import MongoClient
from api import api_bp  # Importando o Blueprint da API
from pymongo import MongoClient
from pymongo.server_api import ServerApi

app = Flask(__name__)

# Configuração do MongoDB
uri = "mongodb+srv://tccaplicativomanutencao:Aa194223@frotalizedb.oenoa.mongodb.net/?retryWrites=true&w=majority&appName=FrotalizeDB"
client = MongoClient(uri, server_api=ServerApi('1'))
db = client.frotalizeDB  # Acesse o banco de dados desejado, se necessário

try:
    client.admin.command('ping')
    print("Pingou sua implantação. Você se conectou com sucesso ao MongoDB!")
except Exception as e:
    print("Erro de conexão:", e)

# Registrando o Blueprint da API
app.register_blueprint(api_bp, url_prefix='/api')

@app.route('/health', methods=['GET'])
def health_check():
    """Rota de health check com verificação da conexão com o banco de dados."""
    try:
        # Tentativa de obter uma coleção como forma de verificar a conexão
        db.list_collection_names()  # Isso dispara uma consulta simples ao banco de dados
        return jsonify({"status": "UP", "database": "Connected"}), 200
    except Exception as e:
        return jsonify({"status": "DOWN", "error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
