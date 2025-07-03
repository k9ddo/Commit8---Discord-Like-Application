from flask import Blueprint, request, jsonify
import bcrypt
import jwt
from datetime import datetime, timedelta
from models import db, User

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

def generate_token(user_id):
    payload = {
        'user_id': user_id,
        'exp': datetime.utcnow() + timedelta(days=1)
    }
    return jwt.encode(payload, 'your-secret-key', algorithm='HS256')

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    
    # Validate required fields
    if not all(k in data for k in ('username', 'email', 'password')):
        return jsonify({'error': 'Missing required fields'}), 400
        
    # Check if user already exists
    if User.query.filter((User.username == data['username']) | 
                        (User.email == data['email'])).first():
        return jsonify({'error': 'Username or email already exists'}), 409
    
    # Hash password
    password_hash = bcrypt.hashpw(data['password'].encode('utf-8'), bcrypt.gensalt())
    
    # Create new user
    new_user = User(
        username=data['username'],
        email=data['email'],
        password_hash=password_hash.decode('utf-8'),
        status='online'
    )
    
    try:
        db.session.add(new_user)
        db.session.commit()
        token = generate_token(new_user.id)
        return jsonify({
            'token': token,
            'user': {
                'id': new_user.id,
                'username': new_user.username,
                'email': new_user.email
            }
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    
    if not all(k in data for k in ('username', 'password')):
        return jsonify({'error': 'Missing username or password'}), 400
    
    user = User.query.filter_by(username=data['username']).first()
    
    if user and bcrypt.checkpw(data['password'].encode('utf-8'), 
                             user.password_hash.encode('utf-8')):
        token = generate_token(user.id)
        return jsonify({
            'token': token,
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email
            }
        }), 200
    
    return jsonify({'error': 'Invalid credentials'}), 401

@auth_bp.route('/me', methods=['GET'])
def get_current_user():
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({'error': 'No token provided'}), 401
    
    token = auth_header.split(' ')[1]
    try:
        payload = jwt.decode(token, 'your-secret-key', algorithms=['HS256'])
        user = User.query.get(payload['user_id'])
        if not user:
            return jsonify({'error': 'User not found'}), 404
            
        return jsonify({
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'status': user.status,
                'avatar_url': user.avatar_url
            }
        }), 200
    except jwt.ExpiredSignatureError:
        return jsonify({'error': 'Token has expired'}), 401
    except jwt.InvalidTokenError:
        return jsonify({'error': 'Invalid token'}), 401

@auth_bp.route('/logout', methods=['POST'])
def logout():
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({'error': 'No token provided'}), 401
    
    token = auth_header.split(' ')[1]
    try:
        payload = jwt.decode(token, 'your-secret-key', algorithms=['HS256'])
        user = User.query.get(payload['user_id'])
        if user:
            user.status = 'offline'
            db.session.commit()
        return jsonify({'message': 'Successfully logged out'}), 200
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        return jsonify({'error': 'Invalid token'}), 401
