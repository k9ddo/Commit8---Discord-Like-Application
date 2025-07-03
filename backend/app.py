from flask import Flask
from flask_cors import CORS
from flask_socketio import SocketIO
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'  # Change in production
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///commi8.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

CORS(app, resources={r"/api/*": {"origins": "http://localhost:8000"}})
db = SQLAlchemy(app)
socketio = SocketIO(app, cors_allowed_origins="http://localhost:8000")

# Initialize models with the app context
with app.app_context():
    from models import User, Server, Channel, Message, server_members
    
    # Import routes after models are initialized
    from routes.auth import auth_bp
    from routes.servers import servers_bp
    from routes.channels import channels_bp
    
    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(servers_bp)
    app.register_blueprint(channels_bp)
    
    # Create all tables
    db.create_all()

# Import socket handlers
from sockets import socketio as socket_handlers

if __name__ == '__main__':
    socketio.run(app, debug=True, port=5000, host='0.0.0.0')
