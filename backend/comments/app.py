import os
from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv
from pathlib import Path

# Load .env from parent directory (backend/.env)
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(env_path)

def create_app():
    app = Flask(__name__)
    CORS(app, origins=os.getenv("CORS_ORIGINS", "*").split(","), supports_credentials=True)

    # Register routes
    from controllers.comment_controller import comment_bp
    app.register_blueprint(comment_bp)

    return app

if __name__ == "__main__":
    app = create_app()
    port = "5008"
    print(f"Comments microservice running on port {port}")
    
    # Debug: Print environment variables
    print(f"SUPABASE_URL: {os.getenv('SUPABASE_URL', 'NOT SET')[:30]}...")
    print(f"SUPABASE_SERVICE_KEY: {'SET' if os.getenv('SUPABASE_SERVICE_KEY') else 'NOT SET'}")
    
    app.run(host="0.0.0.0", port=int(port), debug=True)