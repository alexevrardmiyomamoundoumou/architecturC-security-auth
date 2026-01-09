from config import Config
from pymongo import MongoClient
from datetime import datetime

# Connexion MongoDB
client = MongoClient(Config.MONGO_URI)
db = client.get_database()

def create_rule(rule_data):
    """Créer une règle d'alerte"""
    rule_data["active"] = True
    db.alert_rules.insert_one(rule_data)

def get_rules():
    """Retourne toutes les règles"""
    rules = list(db.alert_rules.find())
    for r in rules:
        r["_id"] = str(r["_id"])
    return rules

def get_history():
    """Retourne l'historique des alertes"""
    history = list(db.alert_history.find().sort("triggered_at", -1))
    for h in history:
        h["_id"] = str(h["_id"])
        if "triggered_at" in h:
            h["triggered_at"] = h["triggered_at"].strftime("%Y-%m-%d %H:%M:%S")
    return history
