from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_socketio import SocketIO, emit, join_room, leave_room
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
from datetime import datetime, timedelta
import os
from functools import wraps

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-change-this-in-production'
socketio = SocketIO(app, cors_allowed_origins="*")

# Database setup
def init_db():
    """Initialize the database with required tables"""
    conn = sqlite3.connect('messaging.db')
    cursor = conn.cursor()
    
    # Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Messages table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sender_id INTEGER NOT NULL,
            receiver_id INTEGER NOT NULL,
            message_content TEXT NOT NULL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_read BOOLEAN DEFAULT 0,
            FOREIGN KEY (sender_id) REFERENCES users (id),
            FOREIGN KEY (receiver_id) REFERENCES users (id)
        )
    ''')
    
    # Rooms table for group chats
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS rooms (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            created_by INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (created_by) REFERENCES users (id)
        )
    ''')
    
    # Room members table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS room_members (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            room_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (room_id) REFERENCES rooms (id),
            FOREIGN KEY (user_id) REFERENCES users (id),
            UNIQUE(room_id, user_id)
        )
    ''')
    
    conn.commit()
    conn.close()

def get_db_connection():
    """Get database connection"""
    conn = sqlite3.connect('messaging.db')
    conn.row_factory = sqlite3.Row
    return conn

def login_required(f):
    """Decorator to require login for routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def update_last_seen(user_id):
    """Update user's last seen timestamp"""
    conn = get_db_connection()
    conn.execute('UPDATE users SET last_seen = ? WHERE id = ?', 
                (datetime.now(), user_id))
    conn.commit()
    conn.close()

# Routes
@app.route('/')
def index():
    """Home page - redirect to login if not authenticated"""
    if 'user_id' in session:
        return redirect(url_for('chat'))
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    """User registration"""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        
        if not username or not password:
            flash('Username and password are required.', 'error')
            return render_template('register.html')
        
        if password != confirm_password:
            flash('Passwords do not match.', 'error')
            return render_template('register.html')
        
        if len(password) < 6:
            flash('Password must be at least 6 characters long.', 'error')
            return render_template('register.html')
        
        conn = get_db_connection()
        
        # Check if username already exists
        existing_user = conn.execute('SELECT id FROM users WHERE username = ?', (username,)).fetchone()
        if existing_user:
            flash('Username already exists. Please choose a different one.', 'error')
            conn.close()
            return render_template('register.html')
        
        # Create new user
        password_hash = generate_password_hash(password)
        cursor = conn.execute('INSERT INTO users (username, password_hash) VALUES (?, ?)', 
                            (username, password_hash))
        user_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login"""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
        conn.close()
        
        if user and check_password_hash(user['password_hash'], password):
            session['user_id'] = user['id']
            session['username'] = user['username']
            update_last_seen(user['id'])
            flash(f'Welcome back, {username}!', 'success')
            return redirect(url_for('chat'))
        else:
            flash('Invalid username or password.', 'error')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    """User logout"""
    update_last_seen(session['user_id'])
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

@app.route('/chat')
@login_required
def chat():
    """Main chat interface"""
    conn = get_db_connection()
    
    # Get all users except current user
    users = conn.execute('''
        SELECT id, username, last_seen 
        FROM users 
        WHERE id != ? 
        ORDER BY username
    ''', (session['user_id'],)).fetchall()
    
    # Get recent conversations
    recent_conversations = conn.execute('''
        SELECT DISTINCT 
            CASE 
                WHEN m.sender_id = ? THEN m.receiver_id 
                ELSE m.sender_id 
            END as other_user_id,
            u.username as other_username,
            m.message_content as last_message,
            m.timestamp as last_message_time
        FROM messages m
        JOIN users u ON (
            CASE 
                WHEN m.sender_id = ? THEN m.receiver_id 
                ELSE m.sender_id 
            END = u.id
        )
        WHERE m.sender_id = ? OR m.receiver_id = ?
        ORDER BY m.timestamp DESC
    ''', (session['user_id'], session['user_id'], session['user_id'], session['user_id'])).fetchall()
    
    conn.close()
    
    return render_template('chat.html', 
                         users=users, 
                         recent_conversations=recent_conversations,
                         current_user=session['username'])

@app.route('/messages/<int:user_id>')
@login_required
def get_messages(user_id):
    """Get messages between current user and another user"""
    conn = get_db_connection()
    
    # Get the other user's info
    other_user = conn.execute('SELECT username FROM users WHERE id = ?', (user_id,)).fetchone()
    if not other_user:
        return jsonify({'error': 'User not found'}), 404
    
    # Get messages between the two users
    messages = conn.execute('''
        SELECT m.*, u.username as sender_username
        FROM messages m
        JOIN users u ON m.sender_id = u.id
        WHERE (m.sender_id = ? AND m.receiver_id = ?) 
           OR (m.sender_id = ? AND m.receiver_id = ?)
        ORDER BY m.timestamp ASC
    ''', (session['user_id'], user_id, user_id, session['user_id'])).fetchall()
    
    # Mark messages as read
    conn.execute('''
        UPDATE messages 
        SET is_read = 1 
        WHERE sender_id = ? AND receiver_id = ? AND is_read = 0
    ''', (user_id, session['user_id']))
    conn.commit()
    conn.close()
    
    return jsonify([dict(msg) for msg in messages])

@app.route('/send_message', methods=['POST'])
@login_required
def send_message():
    """Send a message to another user"""
    data = request.get_json()
    receiver_id = data.get('receiver_id')
    message_content = data.get('message_content')
    
    if not receiver_id or not message_content:
        return jsonify({'error': 'Missing receiver_id or message_content'}), 400
    
    conn = get_db_connection()
    
    # Check if receiver exists
    receiver = conn.execute('SELECT username FROM users WHERE id = ?', (receiver_id,)).fetchone()
    if not receiver:
        return jsonify({'error': 'Receiver not found'}), 404
    
    # Insert message
    cursor = conn.execute('''
        INSERT INTO messages (sender_id, receiver_id, message_content)
        VALUES (?, ?, ?)
    ''', (session['user_id'], receiver_id, message_content))
    
    message_id = cursor.lastrowid
    conn.commit()
    
    # Get the inserted message with sender info
    message = conn.execute('''
        SELECT m.*, u.username as sender_username
        FROM messages m
        JOIN users u ON m.sender_id = u.id
        WHERE m.id = ?
    ''', (message_id,)).fetchone()
    
    conn.close()
    
    # Emit to Socket.IO for real-time delivery
    socketio.emit('new_message', dict(message), room=f'user_{receiver_id}')
    
    return jsonify(dict(message))

@app.route('/online_users')
@login_required
def get_online_users():
    """Get list of online users (active in last 5 minutes)"""
    conn = get_db_connection()
    five_minutes_ago = datetime.now() - timedelta(minutes=5)
    
    online_users = conn.execute('''
        SELECT id, username, last_seen
        FROM users
        WHERE last_seen > ? AND id != ?
        ORDER BY username
    ''', (five_minutes_ago, session['user_id'])).fetchall()
    
    conn.close()
    return jsonify([dict(user) for user in online_users])

# Socket.IO events
@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    if 'user_id' in session:
        join_room(f'user_{session["user_id"]}')
        update_last_seen(session['user_id'])
        emit('user_connected', {'user_id': session['user_id'], 'username': session['username']})

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    if 'user_id' in session:
        update_last_seen(session['user_id'])
        emit('user_disconnected', {'user_id': session['user_id'], 'username': session['username']})

@socketio.on('typing')
def handle_typing(data):
    """Handle typing indicator"""
    receiver_id = data.get('receiver_id')
    if receiver_id:
        emit('user_typing', {
            'user_id': session['user_id'],
            'username': session['username']
        }, room=f'user_{receiver_id}')

@socketio.on('stop_typing')
def handle_stop_typing(data):
    """Handle stop typing indicator"""
    receiver_id = data.get('receiver_id')
    if receiver_id:
        emit('user_stop_typing', {
            'user_id': session['user_id'],
            'username': session['username']
        }, room=f'user_{receiver_id}')

if __name__ == '__main__':
    init_db()
    # Get port from environment variable (for cloud hosting) or use 8080
    port = int(os.environ.get('PORT', 8080))
    socketio.run(app, debug=False, host='0.0.0.0', port=port) 