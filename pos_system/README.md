# 💬 Real-time Messaging System

A complete real-time messaging system built with Python, Flask, and Flask-SocketIO that allows multiple users to chat with each other in real-time.

## ✨ Features

- **🔐 User Authentication**: Secure registration and login system with password hashing
- **💬 Real-time Messaging**: Instant message delivery using WebSocket connections
- **👥 Private Messaging**: Direct messages between users
- **📱 Online Status**: See who's currently online (active in last 5 minutes)
- **💭 Typing Indicators**: Real-time typing notifications
- **📚 Message History**: Persistent message storage and retrieval
- **🎨 Modern UI**: Clean, responsive interface with Bootstrap
- **🗄️ SQLite Database**: Lightweight data persistence
- **🔒 Session Management**: Secure user sessions

## 🚀 Quick Start

### Prerequisites

- Python 3.7 or higher
- pip (Python package installer)

### Installation

1. **Clone or download the project files**

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**:
   ```bash
   python app.py
   ```

4. **Open your browser** and go to:
   ```
   http://localhost:5000
   ```

## 📖 Usage Guide

### 1. Registration
- Click "Register here" on the login page
- Choose a unique username
- Set a password (minimum 6 characters)
- Confirm your password

### 2. Login
- Enter your username and password
- Click "Login"

### 3. Chat Interface
- **All Users Tab**: See all registered users with online status
- **Recent Tab**: View your recent conversations
- Click on any user to start chatting
- Type your message and press Enter or click the send button

### 4. Real-time Features
- **Instant Delivery**: Messages appear immediately for both sender and receiver
- **Typing Indicators**: See when someone is typing
- **Online Status**: Green dots indicate users active in the last 5 minutes
- **Message History**: All conversations are saved and accessible

## 🏗️ Architecture

### Backend (Flask)
- **app.py**: Main Flask application with all routes and Socket.IO events
- **Database**: SQLite with tables for users, messages, and rooms
- **Authentication**: Session-based with password hashing
- **Real-time**: Flask-SocketIO for WebSocket connections

### Frontend (HTML/CSS/JavaScript)
- **Bootstrap 5**: Responsive UI framework
- **Socket.IO Client**: Real-time communication
- **Vanilla JavaScript**: Dynamic interactions and message handling

### Database Schema

#### Users Table
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### Messages Table
```sql
CREATE TABLE messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sender_id INTEGER NOT NULL,
    receiver_id INTEGER NOT NULL,
    message_content TEXT NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_read BOOLEAN DEFAULT 0,
    FOREIGN KEY (sender_id) REFERENCES users (id),
    FOREIGN KEY (receiver_id) REFERENCES users (id)
);
```

## 🔧 API Endpoints

### Authentication
- `GET /register` - Registration page
- `POST /register` - Create new user account
- `GET /login` - Login page
- `POST /login` - Authenticate user
- `GET /logout` - Logout user

### Messaging
- `GET /chat` - Main chat interface
- `GET /messages/<user_id>` - Get messages with specific user
- `POST /send_message` - Send a message
- `GET /online_users` - Get list of online users

### WebSocket Events
- `connect` - User connects to chat
- `disconnect` - User disconnects
- `typing` - User starts typing
- `stop_typing` - User stops typing
- `new_message` - New message received

## 🧪 Testing with Multiple Users

1. **Start the server**:
   ```bash
   python app.py
   ```

2. **Open multiple browser windows/tabs** to `http://localhost:5000`

3. **Register different users** in each window:
   - User 1: `alice` / `password123`
   - User 2: `bob` / `password123`
   - User 3: `charlie` / `password123`

4. **Start chatting**:
   - Select a user from the sidebar
   - Send messages
   - See real-time delivery and typing indicators

## 🔒 Security Features

- **Password Hashing**: Passwords are hashed using Werkzeug's security functions
- **Session Management**: Secure session handling with Flask sessions
- **SQL Injection Protection**: Parameterized queries prevent SQL injection
- **XSS Protection**: HTML escaping in message display
- **CSRF Protection**: Form-based CSRF protection (can be enhanced)

## 🚀 Deployment

### 🌐 **Cloud Deployment (Recommended)**

Want to make your messaging system accessible to everyone? Deploy it to the cloud!

**Quick Deploy Options:**
- **Render.com** (Free) - See `deploy_to_render.md` for detailed instructions
- **Railway.app** (Free) - Similar to Render
- **Heroku** (Requires credit card verification)

**After deployment, anyone can access your messaging system from anywhere!**

### Local Development
```bash
python app.py
```

### Production Deployment
For production, consider:
- Using a production WSGI server (Gunicorn, uWSGI)
- Setting up a proper database (PostgreSQL, MySQL)
- Using environment variables for sensitive data
- Setting up HTTPS
- Using a reverse proxy (Nginx)

Example with Gunicorn:
```bash
pip install gunicorn
gunicorn -k gevent -w 1 --bind 0.0.0.0:5000 app:app
```

## 📁 Project Structure

```
messaging-system/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── README.md             # This file
├── messaging.db          # SQLite database (created automatically)
└── templates/            # HTML templates
    ├── base.html         # Base template
    ├── login.html        # Login page
    ├── register.html     # Registration page
    └── chat.html         # Main chat interface
```

## 🐛 Troubleshooting

### Common Issues

1. **Port already in use**:
   ```bash
   # Change port in app.py or kill existing process
   lsof -ti:5000 | xargs kill -9
   ```

2. **Database errors**:
   ```bash
   # Delete and recreate database
   rm messaging.db
   python app.py
   ```

3. **Socket.IO connection issues**:
   - Check browser console for errors
   - Ensure no firewall blocking WebSocket connections
   - Try different browser

4. **Dependencies not found**:
   ```bash
   pip install -r requirements.txt --upgrade
   ```

### Browser Compatibility
- Chrome/Chromium (recommended)
- Firefox
- Safari
- Edge

## 🔮 Future Enhancements

- **Group Chats**: Create and manage group conversations
- **File Sharing**: Send images, documents, and files
- **Message Encryption**: End-to-end encryption for messages
- **Push Notifications**: Browser notifications for new messages
- **Message Search**: Search through message history
- **User Profiles**: Profile pictures and status messages
- **Message Reactions**: Like, heart, or react to messages
- **Voice/Video Calls**: WebRTC integration
- **Mobile App**: React Native or Flutter mobile app

## 📄 License

This project is open source and available under the MIT License.

## 🤝 Contributing

Feel free to contribute by:
- Reporting bugs
- Suggesting new features
- Submitting pull requests
- Improving documentation

---

**Happy Chatting! 💬✨** 