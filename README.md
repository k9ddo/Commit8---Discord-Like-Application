# Commi8 - Real-time Communication App

A full-stack Discord-like communication platform built with Python (Flask) and Next.js, featuring real-time messaging, server management, and modern UI design.

MADE BY - Bimbisaar Bhate

## 🚀 Features

### Core Functionality
- **User Authentication**: Secure registration and login with bcrypt password hashing
- **Server Management**: Create and join servers (communities)
- **Channel System**: Text and voice channels within servers
- **Real-time Messaging**: Live chat with WebSocket integration
- **Typing Indicators**: See when other users are typing
- **User Status**: Online, offline, idle, and do not disturb statuses
- **Modern UI**: Dark theme with responsive design

### Technical Features
- **JWT Authentication**: Secure token-based authentication
- **Real-time Communication**: Socket.io for instant messaging
- **RESTful API**: Well-structured backend endpoints
- **Responsive Design**: Works on desktop, tablet, and mobile
- **Error Handling**: Comprehensive error handling and validation

## 🛠️ Tech Stack

### Backend
- **Python 3.10+**
- **Flask** - Web framework
- **Flask-SocketIO** - Real-time communication
- **SQLAlchemy** - Database ORM
- **bcrypt** - Password hashing
- **PyJWT** - JSON Web Tokens
- **SQLite** - Database (easily upgradeable to PostgreSQL)

### Frontend
- **Next.js 15** - React framework
- **TypeScript** - Type safety
- **Tailwind CSS** - Styling
- **shadcn/ui** - UI components
- **Socket.io-client** - Real-time client

## 📁 Project Structure

```
commi8/
├── backend/                 # Python Flask backend
│   ├── app.py              # Main application file
│   ├── models.py           # Database models
│   ├── sockets.py          # Socket.io handlers
│   ├── requirements.txt    # Python dependencies
│   └── routes/             # API routes
│       ├── auth.py         # Authentication routes
│       ├── servers.py      # Server management
│       └── channels.py     # Channel operations
├── src/                    # Next.js frontend
│   ├── app/                # App router pages
│   │   ├── login/          # Login page
│   │   ├── register/       # Registration page
│   │   ├── dashboard/      # Main dashboard
│   │   └── server/         # Server and channel pages
│   ├── components/         # React components
│   │   └── ui/             # shadcn/ui components
│   └── hooks/              # Custom React hooks
│       └── use-socket.ts   # Socket.io integration
├── package.json            # Node.js dependencies
├── tailwind.config.js      # Tailwind configuration
└── README.md              # This file
```

## 🚀 Getting Started

### Prerequisites
- **Node.js 18+**
- **Python 3.10+**
- **pip** (Python package manager)
- **npm** or **yarn**

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd commi8
   ```

2. **Install frontend dependencies**
   ```bash
   npm install
   ```

3. **Install backend dependencies**
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

### Running the Application

1. **Start the backend server**
   ```bash
   cd backend
   python app.py
   ```
   The backend will run on `http://localhost:5000`

2. **Start the frontend development server**
   ```bash
   npm run dev
   ```
   The frontend will run on `http://localhost:8000`

3. **Open your browser**
   Navigate to `http://localhost:8000` to access the application

## 📖 Usage

### Getting Started
1. **Register**: Create a new account on the registration page
2. **Login**: Sign in with your credentials
3. **Create Server**: Click the "+" button to create a new server
4. **Create Channels**: Add text or voice channels to your server
5. **Invite Users**: Share your server with others using the invite feature
6. **Start Chatting**: Begin real-time conversations in text channels

### Key Features
- **Real-time Messaging**: Messages appear instantly across all connected clients
- **Server Management**: Organize conversations into servers and channels
- **User Profiles**: Customize your profile and status
- **Responsive Design**: Use on any device with a modern web browser

## 🔧 API Endpoints

### Authentication
- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User login
- `GET /api/auth/me` - Get current user info

### Servers
- `GET /api/servers` - Get user's servers
- `POST /api/servers` - Create new server
- `GET /api/servers/:id` - Get server details
- `POST /api/servers/:id/invite` - Invite user to server

### Channels
- `POST /api/channels/:serverId/create` - Create channel
- `GET /api/channels/:id` - Get channel details
- `POST /api/channels/:id/messages` - Send message

## 🔌 Socket Events

### Client to Server
- `join_server` - Join a server room
- `join_channel` - Join a channel room
- `message` - Send a message
- `typing` - Send typing indicator

### Server to Client
- `new_message` - Receive new message
- `user_typing` - User typing notification
- `user_status_change` - User status update

## 🎨 UI Components

The application uses a modern, dark-themed design with:
- **Responsive Layout**: Adapts to different screen sizes
- **Dark Mode**: Easy on the eyes for long conversations
- **Modern Typography**: Clean, readable fonts
- **Smooth Animations**: Subtle transitions and hover effects
- **Accessible Design**: Keyboard navigation and screen reader support

## 🔒 Security Features

- **Password Hashing**: bcrypt for secure password storage
- **JWT Tokens**: Secure authentication tokens
- **CORS Protection**: Configured for secure cross-origin requests
- **Input Validation**: Server-side validation for all inputs
- **SQL Injection Prevention**: SQLAlchemy ORM protection

## 🚀 Deployment

### Backend Deployment
1. Set environment variables for production
2. Use a production WSGI server like Gunicorn
3. Configure a reverse proxy (nginx)
4. Use PostgreSQL for production database

### Frontend Deployment
1. Build the Next.js application: `npm run build`
2. Deploy to platforms like Vercel, Netlify, or custom server
3. Update API endpoints for production backend

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Commit your changes: `git commit -am 'Add feature'`
4. Push to the branch: `git push origin feature-name`
5. Submit a pull request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🐛 Known Issues

- Voice chat implementation is basic and may need WebRTC improvements
- File upload functionality needs implementation
- Mobile responsiveness could be enhanced for smaller screens

## 🔮 Future Enhancements

- **Voice Chat**: Full WebRTC implementation for voice channels
- **File Sharing**: Upload and share images, documents, and other files
- **Custom Emojis**: Server-specific emoji support
- **Message Threads**: Reply to specific messages
- **User Roles**: Advanced permission system
- **Push Notifications**: Browser notifications for new messages
- **Message Search**: Search through message history
- **Dark/Light Theme Toggle**: User preference for theme

## 📞 Support

If you encounter any issues or have questions:
1. Check the existing issues in the repository
2. Create a new issue with detailed information
3. Include steps to reproduce any bugs

---

**Built with ❤️ using Python, Flask, Next.js, and modern web technologies.**
