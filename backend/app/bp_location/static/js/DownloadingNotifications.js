// Socket.IO Client-Side Connection for Auris Notification System

const AurisNotification = (function() {
    // Private properties
    const _socket = io.connect('http://127.0.0.1:5000');

    // Private methods
    function _onConnect() {
        console.log('Socket connected!');
        _socket.emit('join', { user_id: window.currentUser });
    }

    function _onNotification(notification_data) {
        console.log('Notification received:', notification_data);
        alert(notification_data.content);
        // Redirect to a certain page after clicking 'OK'
        window.location.href = REDIRECT_URL;
    }

    // Initialization and event binding
    _socket.on('connect', _onConnect);
    _socket.on('notification', _onNotification);

    // Public methods and properties (if any can be added here)

    return {
        // For now, we don't have any public methods or properties.
    };
})();
