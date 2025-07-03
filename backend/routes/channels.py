from flask import Blueprint, request, jsonify
from models import db, Channel, Server, User, Message
from functools import wraps
import jwt

channels_bp = Blueprint('channels', __name__, url_prefix='/api/channels')

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

@channels_bp.route('/<int:server_id>/create', methods=['POST'])
@token_required
def create_channel(current_user, server_id):
    server = Server.query.get(server_id)
    if not server:
        return jsonify({'error': 'Server not found'}), 404
    
    if current_user.id != server.owner_id:
        return jsonify({'error': 'Only server owner can create channels'}), 403
    
    data = request.get_json()
    if not all(k in data for k in ('name', 'type')):
        return jsonify({'error': 'Channel name and type are required'}), 400
    
    if data['type'] not in ['text', 'voice']:
        return jsonify({'error': 'Invalid channel type'}), 400
    
    try:
        new_channel = Channel(
            name=data['name'],
            type=data['type'],
            server_id=server_id
        )
        db.session.add(new_channel)
        db.session.commit()
        
        return jsonify({
            'channel': {
                'id': new_channel.id,
                'name': new_channel.name,
                'type': new_channel.type,
                'server_id': new_channel.server_id
            }
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@channels_bp.route('/<int:channel_id>', methods=['GET'])
@token_required
def get_channel(current_user, channel_id):
    channel = Channel.query.get(channel_id)
    if not channel:
        return jsonify({'error': 'Channel not found'}), 404
    
    server = Server.query.get(channel.server_id)
    if current_user not in server.members:
        return jsonify({'error': 'Access denied'}), 403
    
    # Get messages with pagination
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 50, type=int)
    
    messages = Message.query.filter_by(channel_id=channel_id)\
        .order_by(Message.created_at.desc())\
        .paginate(page=page, per_page=per_page)
    
    return jsonify({
        'channel': {
            'id': channel.id,
            'name': channel.name,
            'type': channel.type,
            'server_id': channel.server_id,
            'messages': [{
                'id': msg.id,
                'content': msg.content,
                'created_at': msg.created_at.isoformat(),
                'edited_at': msg.edited_at.isoformat() if msg.edited_at else None,
                'author': {
                    'id': msg.author.id,
                    'username': msg.author.username,
                    'avatar_url': msg.author.avatar_url
                },
                'attachments': [{
                    'id': att.id,
                    'filename': att.filename,
                    'file_url': att.file_url
                } for att in msg.attachments]
            } for msg in messages.items],
            'pagination': {
                'total': messages.total,
                'pages': messages.pages,
                'current_page': messages.page,
                'per_page': messages.per_page
            }
        }
    }), 200

@channels_bp.route('/<int:channel_id>', methods=['DELETE'])
@token_required
def delete_channel(current_user, channel_id):
    channel = Channel.query.get(channel_id)
    if not channel:
        return jsonify({'error': 'Channel not found'}), 404
    
    server = Server.query.get(channel.server_id)
    if current_user.id != server.owner_id:
        return jsonify({'error': 'Only server owner can delete channels'}), 403
    
    try:
        db.session.delete(channel)
        db.session.commit()
        return jsonify({'message': 'Channel deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@channels_bp.route('/<int:channel_id>/messages', methods=['POST'])
@token_required
def send_message(current_user, channel_id):
    channel = Channel.query.get(channel_id)
    if not channel:
        return jsonify({'error': 'Channel not found'}), 404
    
    if channel.type != 'text':
        return jsonify({'error': 'Can only send messages in text channels'}), 400
    
    server = Server.query.get(channel.server_id)
    if current_user not in server.members:
        return jsonify({'error': 'Access denied'}), 403
    
    data = request.get_json()
    if 'content' not in data:
        return jsonify({'error': 'Message content is required'}), 400
    
    try:
        new_message = Message(
            content=data['content'],
            channel_id=channel_id,
            user_id=current_user.id
        )
        db.session.add(new_message)
        db.session.commit()
        
        # The actual message broadcast will be handled by SocketIO
        return jsonify({
            'message': {
                'id': new_message.id,
                'content': new_message.content,
                'created_at': new_message.created_at.isoformat(),
                'author': {
                    'id': current_user.id,
                    'username': current_user.username,
                    'avatar_url': current_user.avatar_url
                }
            }
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
