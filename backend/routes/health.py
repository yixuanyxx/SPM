# sample 
# python files in routes will be where we write the functions, app.py will import these routes and call these functions
from flask import Blueprint, jsonify

health_bp = Blueprint("health", __name__)

@health_bp.route("/health", methods=["GET"])
def health():
    return jsonify({"ok": True})
