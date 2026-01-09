from flask import Blueprint, render_template

pages_bp = Blueprint("pages", __name__)

@pages_bp.route("/")
def home():
    return render_template("index.html")

@pages_bp.route("/results")
def results():
    return render_template("results.html")

@pages_bp.route("/search")
def search():
    return render_template("search.html")

@pages_bp.route("/upload")
def upload():
    return render_template("upload.html")

@pages_bp.route("/history")
def history():
    return render_template("history.html")