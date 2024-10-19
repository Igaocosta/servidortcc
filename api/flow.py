# api/flow.py
from flask import Blueprint, request, jsonify
import requests
from typing import Optional
from config import BASEAPIURL, FLOW_ID

flow_bp = Blueprint('flow', __name__)

TWEAKS = {
    "ChatInput-tXWsY": {},
    "ParseData-M2CvI": {},
    "Prompt-J90mM": {},
    "ChatOutput-HKNnk": {},
    "SplitText-AC1Su": {},
    "File-y3ELa": {},
    "OpenAIEmbeddings-tf2Bh": {},
    "OpenAIEmbeddings-Dr3zq": {},
    "OpenAIModel-z6XWq": {},
    "AstraDB-5KsIu": {},
    "AstraDB-ZNpJk": {}
}

def run_flow(message: str, endpoint: str, tweaks: Optional[dict] = None, api_key: Optional[str] = None) -> dict:
    api_url = f"{BASEAPIURL}/api/v1/run/{endpoint}"
    
    payload = {
        "input_value": message,
        "output_type": "chat",
        "input_type": "chat",
    }
    
    if tweaks:
        payload["tweaks"] = tweaks
    headers = {"x-api-key": api_key} if api_key else None

    try:
        response = requests.post(api_url, json=payload, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}

@flow_bp.route('/run_flow', methods=['GET'])
def isOn():
    return jsonify({"message": "Server is online!"}), 200

@flow_bp.route('/run_flow', methods=['POST'])
def run_flow_api():
    data = request.get_json()

    if not data or 'message' not in data:
        return jsonify({"error": "Please provide a message in the request body"}), 400

    message = data['message']
    endpoint = data.get('endpoint', FLOW_ID)
    tweaks = data.get('tweaks', TWEAKS)
    api_key = data.get('api_key', None)

    result = run_flow(message=message, endpoint=endpoint, tweaks=tweaks, api_key=api_key)
    
    return jsonify(result)
