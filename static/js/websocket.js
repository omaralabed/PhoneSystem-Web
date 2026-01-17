/**
 * WebSocket Connection and Real-time Updates
 * Handles Socket.IO connection for live line status updates
 */

class WebSocketManager {
    constructor() {
        this.socket = null;
        this.connected = false;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 10;
        this.callbacks = {};
    }
    
    connect() {
        console.log('Connecting to WebSocket...');
        
        // Initialize Socket.IO connection
        this.socket = io();
        
        // Connection events
        this.socket.on('connect', () => {
            console.log('WebSocket connected');
            this.connected = true;
            this.reconnectAttempts = 0;
            
            // Subscribe to all line updates
            this.socket.emit('subscribe', { lines: [1, 2, 3, 4, 5, 6, 7, 8] });
            
            // Trigger connected callback
            if (this.callbacks.onConnect) {
                this.callbacks.onConnect();
            }
        });
        
        this.socket.on('disconnect', () => {
            console.log('WebSocket disconnected');
            this.connected = false;
            
            if (this.callbacks.onDisconnect) {
                this.callbacks.onDisconnect();
            }
        });
        
        this.socket.on('connect_error', (error) => {
            console.error('WebSocket connection error:', error);
            this.reconnectAttempts++;
            
            if (this.reconnectAttempts >= this.maxReconnectAttempts) {
                console.error('Max reconnect attempts reached');
            }
        });
        
        // Line status updates
        this.socket.on('line_status', (data) => {
            console.log('Line status update:', data);
            
            if (this.callbacks.onLineStatus) {
                this.callbacks.onLineStatus(data);
            }
        });
        
        // SIP registration updates
        this.socket.on('sip_registration', (data) => {
            console.log('SIP registration update:', data);
            
            if (this.callbacks.onSIPRegistration) {
                this.callbacks.onSIPRegistration(data);
            }
        });
    }
    
    disconnect() {
        if (this.socket) {
            this.socket.disconnect();
            this.socket = null;
            this.connected = false;
        }
    }
    
    on(event, callback) {
        this.callbacks[event] = callback;
    }
}

// Global WebSocket manager instance
const wsManager = new WebSocketManager();
