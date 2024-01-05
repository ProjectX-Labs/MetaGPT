from typing import Dict


class ConnectionManager:
    def __init__(self, socket):
        self.socket = socket
        self.active_connections: Dict[str, object] = {}

    async def connect(self, sid, environ):
        # Store environment data (e.g., user session info) on connection
        self.active_connections[sid] = environ

    async def disconnect(self, sid):
        # Remove the connection from the active connections
        self.active_connections.pop(sid, None)

    async def send_update(self, user_id: str, session_id: str, message: str):
        # Find the socket ID for the given user and AI session ID
        sid = next((sid for sid, environ in self.active_connections.items()
                    if environ.get('user_id') == user_id and environ.get('ai_session_id') == session_id), None)
        if sid:
            # Emit message only to the specific user and AI session
            await self.socket.emit('ai_session_update', message, room=sid)
            # Update AI session's status or message history as needed

    async def receive_message(self, sid, message):
        environ = self.active_connections.get(sid)
        user_id = environ.get('user_id') if environ else None
        session_id = environ.get('ai_session_id') if environ else None

        if user_id and session_id:
            # Handle received message, update AI session as needed
            print(f"Received message from {user_id} in session {session_id}: {message}")
            pass

    # async def broadcast(self, message: str):
    #     # Send a message to all connected clients
    #     await self.socket.emit('broadcast_message', message)

    # # Additional functionality for reconnection handling
    # async def handle_reconnection(self, sid, environ):
    #     # Logic to handle reconnection - can include re-joining rooms or resynchronizing data
    #     pass

