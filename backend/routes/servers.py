from flask import Blueprint, request, jsonify
from models import db, Server, Channel, User
from functools import wraps
import jwt

servers_bp = Blueprint('servers', __name__, url_prefix='/api/servers')

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'error': 'No token provided'}), 401
        
        token = auth_header.split(' ')[1]
        try:
            payload = jwt.decode(token, 'your-secret-key', algorithms=['HS256'])
            user = User.query.get(payload['user_id'])
            if not user:
                return jsonify({'error': 'User not found'}), 404
            return f(user, *args, **kwargs)
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token has expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Invalid token'}), 401
    return decorated

@servers_bp.route('/', methods=['POST'])
@token_required
def create_server(current_user):
    data = request.get_json()
    
    if 'name' not in data:
        return jsonify({'error': 'Server name is required'}), 400
    
    new_server = Server(
        name=data['name'],
        description=data.get('description', ''),
        icon_url=data.get('icon_url'),
        owner_id=current_user.id
    )
    
    try:
        # Add the server
        db.session.add(new_server)
        db.session.flush()  # Get the server ID
        
        # Create default channels
        general_channel = Channel(
            name='general',
            type='text',
            server_id=new_server.id
        )
        voice_channel = Channel(
            name='General Voice',
            type='voice',
            server_id=new_server.id
        )
        
        # Add owner as member
        new_server.members.append(current_user)
        
        db.session.add(general_channel)
        db.session.add(voice_channel)
        db.session.commit()
        
        return jsonify({
            'server': {
                'id': new_server.id,
                'name': new_server.name,
                'description': new_server.description,
                'icon_url': new_server.icon_url,
                'channels': [
                    {'id': general_channel.id, 'name': general_channel.name, 'type': general_channel.type},
                    {'id': voice_channel.id, 'name': voice_channel.name, 'type': voice_channel.type}
                ]
            }
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@servers_bp.route('/', methods=['GET'])
@token_required
def get_user_servers(current_user):
    try:
        servers = current_user.servers
        return jsonify({
            'servers': [{
                'id': server.id,
                'name': server.name,
                'description': server.description,
                'icon_url': server.icon_url,
                'channels': [{
                    'id': channel.id,
                    'name': channel.name,
                    'type': channel.type
                } for channel in server.channels]
            } for server in servers]
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@servers_bp.route('/<int:server_id>', methods=['GET'])
@token_required
def get_server(current_user, server_id):
    server = Server.query.get(server_id)
    if not server:
        return jsonify({'error': 'Server not found'}), 404
    
    if current_user not in server.members:
        return jsonify({'error': 'Access denied'}), 403
    
    return jsonify({
        'server': {
            'id': server.id,
            'name': server.name,
            'description': server.description,
            'icon_url': server.icon_url,
            'channels': [{
                'id': channel.id,
                'name': channel.name,
                'type': channel.type
            } for channel in server.channels],
            'members': [{
                'id': member.id,
                'username': member.username,
                'status': member.status,
                'avatar_url': member.avatar_url
            } for member in server.members]
        }
    }), 200

@servers_bp.route('/<int:server_id>/invite', methods=['POST'])
@token_required
def invite_to_server(current_user, server_id):
    server = Server.query.get(server_id)
    if not server:
        return jsonify({'error': 'Server not found'}), 404
    
    if current_user.id != server.owner_id:
        return jsonify({'error': 'Only server owner can invite users'}), 403
    
    data = request.get_json()
    if 'username' not in data:
        return jsonify({'error': 'Username is required'}), 400
    
    user_to_invite = User.query.filter_by(username=data['username']).first()
    if not user_to_invite:
        return jsonify({'error': 'User not found'}), 404
    
    if user_to_invite in server.members:
        return jsonify({'error': 'User is already a member'}), 400
    
    try:
        server.members.append(user_to_invite)
        db.session.commit()
        return jsonify({'message': f'Successfully invited {user_to_invite.username}'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
