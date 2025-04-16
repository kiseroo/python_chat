import json
import datetime
import threading
from flask import Flask, request, render_template, redirect, url_for, jsonify, session
from message import Message
from chat_history import ChatHistory

# Flask app initialization
app = Flask(__name__)
app.secret_key = 'chat_secret_key'  # For session management

# Chat history and connected clients
chat_history = ChatHistory()
connected_clients = {}  # {username: last_seen_timestamp}
message_queue = []  # Store new messages for polling
last_update_time = datetime.datetime.now()

# Check for inactive clients
def cleanup_inactive_clients():
    while True:
        current_time = datetime.datetime.now()
        inactive_threshold = datetime.timedelta(minutes=5)
        
        for username, last_seen in list(connected_clients.items()):
            if current_time - last_seen > inactive_threshold:
                # Announce user logout
                system_message = Message("Систем", f"{username} чатаас гарлаа.")
                chat_history.add_message(system_message)
                message_queue.append(str(system_message))
                del connected_clients[username]
                
        # Run every 60 seconds
        threading.Event().wait(60)

# Start cleanup thread
cleanup_thread = threading.Thread(target=cleanup_inactive_clients)
cleanup_thread.daemon = True
cleanup_thread.start()

# Routes
@app.route('/')
def index():
    """Main page with login form"""
    if 'username' in session:
        return redirect(url_for('chat'))
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    """Handle login"""
    username = request.form.get('username', '').strip()
    if not username:
        return redirect(url_for('index'))
    
    session['username'] = username
    connected_clients[username] = datetime.datetime.now()
    
    # Announce user login
    system_message = Message("Систем", f"{username} чатад нэвтэрлээ.")
    chat_history.add_message(system_message)
    message_queue.append(str(system_message))
    
    return redirect(url_for('chat'))

@app.route('/logout')
def logout():
    """Handle logout"""
    if 'username' in session:
        username = session['username']
        if username in connected_clients:
            # Announce user logout
            system_message = Message("Систем", f"{username} чатаас гарлаа.")
            chat_history.add_message(system_message)
            message_queue.append(str(system_message))
            del connected_clients[username]
        session.pop('username', None)
    
    return redirect(url_for('index'))

@app.route('/chat')
def chat():
    """Chat page"""
    if 'username' not in session:
        return redirect(url_for('index'))
    
    # Update last seen timestamp
    username = session['username']
    connected_clients[username] = datetime.datetime.now()
    
    return render_template('chat.html', username=username)

@app.route('/send', methods=['POST'])
def send_message():
    """Send a message"""
    if 'username' not in session:
        return jsonify({'status': 'error', 'message': 'Not logged in'})
    
    content = request.form.get('content', '').strip()
    if not content:
        return jsonify({'status': 'error', 'message': 'Empty message'})
    
    username = session['username']
    connected_clients[username] = datetime.datetime.now()
    
    message = Message(username, content)
    chat_history.add_message(message)
    message_queue.append(str(message))
    
    return jsonify({'status': 'success'})

@app.route('/messages')
def get_messages():
    """Get messages - supports long polling"""
    if 'username' not in session:
        return jsonify({'status': 'error', 'message': 'Not logged in'})
    
    username = session['username']
    connected_clients[username] = datetime.datetime.now()
    
    # First load - get history
    if request.args.get('first_load') == 'true':
        history = [str(msg) for msg in chat_history.get_messages()]
        return jsonify({
            'status': 'success',
            'messages': history,
            'users': list(connected_clients.keys())
        })
    
    # Long polling - wait for new messages
    global message_queue
    if message_queue:
        messages = message_queue.copy()
        message_queue = []
        return jsonify({
            'status': 'success', 
            'messages': messages,
            'users': list(connected_clients.keys())
        })
    
    return jsonify({
        'status': 'success', 
        'messages': [],
        'users': list(connected_clients.keys())
    })

@app.route('/active_users')
def active_users():
    """Get list of active users"""
    if 'username' not in session:
        return jsonify({'status': 'error', 'message': 'Not logged in'})
    
    return jsonify({
        'status': 'success',
        'users': list(connected_clients.keys())
    })

if __name__ == '__main__':
    # Create templates directory if it doesn't exist
    import os
    if not os.path.exists('templates'):
        os.makedirs('templates')
    
    app.run(host='0.0.0.0', port=5000, debug=True) 