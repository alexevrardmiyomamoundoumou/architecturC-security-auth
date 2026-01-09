from flask import Blueprint, request, jsonify
from services.alert_service import (
    create_rule, get_rules, get_history
)

alerts_bp = Blueprint("alerts_bp", __name__, url_prefix="/api/alerts")

# Créer une règle
@alerts_bp.route("/rules", methods=["POST"])
def add_rule():
    data = request.json
    create_rule(data)
    return jsonify({"message": "Rule created"}), 201

# Lister toutes les règles
@alerts_bp.route("/rules", methods=["GET"])
def list_rules():
    return jsonify(get_rules())

# Lister l'historique des alertes
@alerts_bp.route("/history", methods=["GET"])
def history():
    return jsonify(get_history())
