from flask_socketio import SocketIO, emit, join_room, leave_room
from flask import request
import jwt
from models import db, User, Message, Channel, Server
from datetime import datetime

socketio = SocketIO()

def get_user_from_token(token):
    try:
        payload = jwt.decode(token, 'your-secret-key', algorithms=['HS256'])
        return User.query.get(payload['user_id'])
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        return None

@socketio.on('connect')
def handle_connect():
    token = request.args.get('token')
    if not token:
        return False
    
    user = get_user_from_token(token)
    if not user:
        return False
    
    user.status = 'online'
    db.session.commit()
    
    # Broadcast user's online status to relevant servers
    for server in user.servers:
        emit('user_status_change', {
            'user_id': user.id,
            'status': 'online'
        }, room=f'server_{server.id}')
    
    return True

@socketio.on('disconnect')
def handle_disconnect():
    token = request.args.get('token')
    if token:
        user = get_user_from_token(token)
        if user:
            user.status = 'offline'
            db.session.commit()
            
            # Broadcast user's offline status
            for server in user.servers:
                emit('user_status_change', {
                    'user_id': user.id,
                    'status': 'offline'
                }, room=f'server_{server.id}')

@socketio.on('join_server')
def handle_join_server(data):
    token = data.get('token')
    server_id = data.get('server_id')
    
    if not token or not server_id:
        return
    
    user = get_user_from_token(token)
    if not user:
        return
    
    server = Server.query.get(server_id)
    if not server or user not in server.members:
        return
    
    join_room(f'server_{server_id}')
    
    # Join all channel rooms in the server
    for channel in server.channels:
        join_room(f'channel_{channel.id}')

@socketio.on('join_channel')
def handle_join_channel(data):
    token = data.get('token')
    channel_id = data.get('channel_id')
    
    if not token or not channel_id:
        return
    
    user = get_user_from_token(token)
    if not user:
        return
    
    channel = Channel.query.get(channel_id)
    if not channel:
        return
    
    server = Server.query.get(channel.server_id)
    if not server or user not in server.members:
        return
    
    join_room(f'channel_{channel_id}')
    
    # For voice channels, broadcast user joined
    if channel.type == 'voice':
        emit('voice_user_joined', {
            'channel_id': channel_id,
            'user': {
                'id': user.id,
                'username': user.username,
                'avatar_url': user.avatar_url
            }
        }, room=f'channel_{channel_id}')

@socketio.on('leave_channel')
def handle_leave_channel(data):
    token = data.get('token')
    channel_id = data.get('channel_id')
    
    if not token or not channel_id:
        return
    
    user = get_user_from_token(token)
    if not user:
        return
    
    channel = Channel.query.get(channel_id)
    if not channel:
        return
    
    leave_room(f'channel_{channel_id}')
    
    # For voice channels, broadcast user left
    if channel.type == 'voice':
        emit('voice_user_left', {
            'channel_id': channel_id,
            'user_id': user.id
        }, room=f'channel_{channel_id}')

@socketio.on('message')
def handle_message(data):
    token = data.get('token')
    channel_id = data.get('channel_id')
    content = data.get('content')
    
    if not all([token, channel_id, content]):
        return
    
    user = get_user_from_token(token)
    if not user:
        return
    
    channel = Channel.query.get(channel_id)
    if not channel or channel.type != 'text':
        return
    
    server = Server.query.get(channel.server_id)
    if not server or user not in server.members:
        return
    
    # Create and save the message
    try:
        new_message = Message(
            content=content,
            channel_id=channel_id,
            user_id=user.id
        )
        db.session.add(new_message)
        db.session.commit()
        
        # Broadcast the message to the channel
        emit('new_message', {
            'message': {
                'id': new_message.id,
                'content': new_message.content,
                'created_at': new_message.created_at.isoformat(),
                'channel_id': channel_id,
                'author': {
                    'id': user.id,
                    'username': user.username,
                    'avatar_url': user.avatar_url
                }
            }
        }, room=f'channel_{channel_id}')
        
    except Exception as e:
        db.session.rollback()
        emit('error', {'message': str(e)}, room=request.sid)

@socketio.on('typing')
def handle_typing(data):
    token = data.get('token')
    channel_id = data.get('channel_id')
    
    if not token or not channel_id:
        return
    
    user = get_user_from_token(token)
    if not user:
        return
    
    channel = Channel.query.get(channel_id)
    if not channel or channel.type != 'text':
        return
    
    # Broadcast typing status to channel
    emit('user_typing', {
        'channel_id': channel_id,
        'user': {
            'id': user.id,
            'username': user.username
        }
    }, room=f'channel_{channel_id}')

# Voice chat signaling
@socketio.on('voice_signal')
def handle_voice_signal(data):
    token = data.get('token')
    channel_id = data.get('channel_id')
    signal_data = data.get('signal')
    target_user_id = data.get('target_user_id')
    
    if not all([token, channel_id, signal_data, target_user_id]):
        return
    
    user = get_user_from_token(token)
    if not user:
        return
    
    channel = Channel.query.get(channel_id)
    if not channel or channel.type != 'voice':
        return
    
    # Forward the WebRTC signal to the target user
    emit('voice_signal', {
        'channel_id': channel_id,
        'from_user_id': user.id,
        'signal': signal_data
    }, room=f'user_{target_user_id}')
