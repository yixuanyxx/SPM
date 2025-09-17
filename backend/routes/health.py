# sample 
# python files in routes will be where we write the functions
from flask import jsonify

def register_health_routes(app):
    @app.route("/health", methods=["GET"])
    def health():
        return jsonify({"ok": True})
