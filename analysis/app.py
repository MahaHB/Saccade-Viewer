import os
import sys
from pathlib import Path
from flask import Flask, render_template, send_from_directory

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from analysis.ipast import ipast_bp
from analysis.fv import fv_bp

app = Flask(__name__, template_folder=BASE_DIR / "templates")
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-key")

app.config["DATA_DIR"] = BASE_DIR / "data"

app.register_blueprint(ipast_bp)
app.register_blueprint(fv_bp)

@app.route("/")
def home():
    return render_template("home.html")


@app.route("/google1792c6511cfba111.html")
def google_verification():
    return send_from_directory(BASE_DIR, "google1792c6511cfba111.html")
if __name__ == "__main__":
    app.run(debug=True)