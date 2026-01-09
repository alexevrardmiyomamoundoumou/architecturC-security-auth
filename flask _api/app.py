from flask import Flask, render_template, jsonify, request
import redis
from pymongo import MongoClient
from datetime import datetime
from flask_cors import CORS
from routes.pages_routes import pages_bp
from werkzeug.utils import secure_filename
from routes.alerts_routes import alerts_bp
import os

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB

ALLOWED_EXTENSIONS = {'csv', 'json'}

app.register_blueprint(alerts_bp)
app.register_blueprint(pages_bp)

# ---------------- Connexion MongoDB sans authentification ----------------
try:
    client = MongoClient("mongodb://localhost:27017/")  # MongoDB sans auth
    db = client["logsdb"]  # ta base locale
    print("Connexion MongoDB OK")
except Exception as e:
    print("Erreur connexion MongoDB :", e)
    db = None

# ---------------- Connexion Redis ----------------
try:
    r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
    r.ping()
    print("Connexion Redis OK")
except redis.exceptions.ConnectionError as e:
    print("Erreur connexion Redis :", e)
    r = None

# ---------------- Logs simulés ----------------
LOGS = [
    {"id": 1, "date": "2026-01-05 10:00:00", "level": "INFO", "service": "auth", "message": "User login successful"},
    {"id": 2, "date": "2026-01-05 10:05:00", "level": "WARN", "service": "payment", "message": "Payment delayed"},
    {"id": 3, "date": "2026-01-05 10:10:00", "level": "ERROR", "service": "database", "message": "Connection failed"},
    {"id": 4, "date": "2026-01-05 10:15:00", "level": "INFO", "service": "auth", "message": "Password changed"},
    {"id": 5, "date": "2026-01-05 10:20:00", "level": "ERROR", "service": "api", "message": "Endpoint timeout"}
]

# ---------------- Routes ----------------
@app.route('/')
def home():
    return render_template('index.html')


@app.route('/api/logs/summary')
def logs_summary():
    counts = {"INFO": 0, "WARN": 0, "ERROR": 0, "total": len(LOGS)}
    for log in LOGS:
        counts[log["level"]] += 1
    dates = [log["date"] for log in LOGS]
    counts_by_time = list(range(1, len(LOGS) + 1))
    return jsonify({
        "INFO": counts["INFO"],
        "WARN": counts["WARN"],
        "ERROR": counts["ERROR"],
        "total": counts["total"],
        "dates": dates,
        "counts": counts_by_time
    })


@app.route('/api/logs/last')
def logs_last():
    return jsonify(sorted(LOGS, key=lambda x: x["date"], reverse=True)[:10])


@app.route('/api/logs/search', methods=['GET'])
def logs_search():
    text = request.args.get('text', '').lower()
    level = request.args.get('level', '')

    # Filtrage des logs
    results = [
        log for log in LOGS
        if (not text or text in log["message"].lower())
        and (not level or log["level"] == level)
    ]

    # Sauvegarde de la recherche dans MongoDB
    if db is not None and (text or level):
        try:
            db.search_history.insert_one({
                "user": "Anonymous","Alex"
                "query": text,
                "level": level if level else "ALL",
                "searched_at": datetime.utcnow()
            })
        except Exception as e:
            print("Erreur sauvegarde historique :", e)

    return jsonify(results)


@app.route('/api/logs/history', methods=['GET'])
def get_history():
    if db is None:
        return {"error": "MongoDB non disponible"}, 500
    history = list(db.search_history.find().sort("searched_at", -1))
    for h in history:
        h["_id"] = str(h["_id"])
        if "searched_at" in h:
            h["searched_at"] = h["searched_at"].strftime("%Y-%m-%d %H:%M:%S")
    return jsonify(history)


@app.route('/api/logs/history', methods=['POST'])
def save_search():
    if db is None:
        return {"error": "MongoDB non disponible"}, 500
    data = request.json
    doc = {
        "user": data.get("user", "anonymous"),
        "query": data.get("query"),
        "level": data.get("level"),
        "searched_at": datetime.utcnow()
    }
    db.search_history.insert_one(doc)
    return {"message": "Historique sauvegardé"}, 201


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/api/logs/upload', methods=['POST'])
def logs_upload():
    files = request.files.getlist('files')
    if not files:
        return jsonify({"error": "Aucun fichier reçu"}), 400

    saved_files = []
    errors = []

    for f in files:
        if f.filename == '' or not allowed_file(f.filename):
            errors.append({"filename": f.filename, "error": "Extension non autorisée ou nom vide"})
            continue

        filename = secure_filename(f.filename)
        filepath = os.path.join(UPLOAD_FOLDER, filename)

        try:
            f.save(filepath)
            saved_files.append(filename)
            if db is not None:
                db.files.insert_one({
                    "filename": filename,
                    "filepath": filepath,
                    "mimetype": f.mimetype,
                    "size": os.path.getsize(filepath),
                    "uploaded_at": datetime.utcnow()
                })
        except Exception as e:
            errors.append({"filename": f.filename, "error": str(e)})

    response = {"saved": saved_files}
    if errors:
        response["errors"] = errors

    status_code = 201 if saved_files else 200
    return jsonify(response), status_code


# ---------------- Lancement ----------------
if __name__ == "__main__":
    app.run(debug=True)
