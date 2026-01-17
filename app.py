#!/usr/bin/env python3
"""
PhoneSystem-Web - Flask Application
Web-based 8-line phone system for broadcast production
"""

import os
import json
import logging
import subprocess
from pathlib import Path
from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO, emit
import threading

from src.sip_engine import SIPEngine
from src.audio_router import AudioRouter
from src.phone_line import LineState

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-change-this'  # Change in production
socketio = SocketIO(app, cors_allowed_origins="*")

# Initialize phone system components
sip_engine = None
audio_router = None

def init_phone_system():
    """Initialize SIP engine and audio router"""
    global sip_engine, audio_router
    
    try:
        # Initialize audio router
        logger.info("Initializing audio router...")
        audio_router = AudioRouter("config/audio_config.json")
        audio_router.start()
        
        # Initialize SIP engine
        logger.info("Initializing SIP engine...")
        sip_engine = SIPEngine(num_lines=8)
        sip_engine.start()
        
        # Register callbacks for real-time updates
        for line_id in range(1, 9):
            line = sip_engine.get_line(line_id)
            line.on_state_change = lambda lid, old, new: on_line_state_change(lid, old, new)
            line.on_audio_route_change = lambda lid, output: on_audio_route_change(lid, output)
        
        logger.info("Phone system initialized successfully")
        return True
        
    except Exception as e:
        logger.error(f"Failed to initialize phone system: {e}")
        return False


def on_line_state_change(line_id, old_state, new_state):
    """Callback for line state changes - broadcast to all clients"""
    line = sip_engine.get_line(line_id)
    socketio.emit('line_status', {
        'line_id': line_id,
        'state': new_state.value,
        'phone_number': line.remote_number or '',
        'caller_id': line.remote_number or '',
        'duration': line.call_duration,
        'audio_channel': line.audio_output.channel
    })


def on_audio_route_change(line_id, audio_output):
    """Callback for audio routing changes"""
    socketio.emit('line_status', {
        'line_id': line_id,
        'audio_channel': audio_output.channel
    })


# ============================================================================
# WEB ROUTES
# ============================================================================

@app.route('/')
def index():
    """Main phone system page"""
    return render_template('index.html')


@app.route('/sip-settings')
def sip_settings():
    """SIP configuration page"""
    return render_template('sip_settings.html')


@app.route('/network-settings')
def network_settings():
    """Network configuration page"""
    return render_template('network_settings.html')


# ============================================================================
# API ENDPOINTS - Lines
# ============================================================================

@app.route('/api/lines', methods=['GET'])
def api_get_all_lines():
    """Get status of all 8 lines"""
    try:
        lines_status = []
        for line_id in range(1, 9):
            line = sip_engine.get_line(line_id)
            lines_status.append({
                'line_id': line_id,
                'state': line.state.value,
                'phone_number': line.remote_number or '',
                'caller_id': line.remote_number or '',
                'duration': line.call_duration,
                'audio_channel': line.audio_output.channel,
                'sip_registered': True  # TODO: Get actual registration status
            })
        return jsonify(lines_status)
    except Exception as e:
        logger.error(f"Error getting lines status: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/lines/<int:line_id>', methods=['GET'])
def api_get_line(line_id):
    """Get status of specific line"""
    try:
        if not 1 <= line_id <= 8:
            return jsonify({'error': 'Invalid line ID'}), 400
        
        line = sip_engine.get_line(line_id)
        return jsonify({
            'line_id': line_id,
            'state': line.state.value,
            'phone_number': line.remote_number or '',
            'caller_id': line.remote_number or '',
            'duration': line.call_duration,
            'audio_channel': line.audio_output.channel,
            'sip_registered': True
        })
    except Exception as e:
        logger.error(f"Error getting line {line_id} status: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/lines/<int:line_id>/dial', methods=['POST'])
def api_dial(line_id):
    """Dial a number on specified line"""
    try:
        if not 1 <= line_id <= 8:
            return jsonify({'error': 'Invalid line ID'}), 400
        
        data = request.get_json()
        phone_number = data.get('phone_number', '').strip()
        
        if not phone_number:
            return jsonify({'error': 'Phone number required'}), 400
        
        success = sip_engine.make_call(line_id, phone_number)
        
        if success:
            return jsonify({'status': 'dialing', 'phone_number': phone_number})
        else:
            return jsonify({'error': 'Failed to dial'}), 500
            
    except Exception as e:
        logger.error(f"Error dialing on line {line_id}: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/lines/<int:line_id>/hangup', methods=['POST'])
def api_hangup(line_id):
    """Hang up call on specified line"""
    try:
        if not 1 <= line_id <= 8:
            return jsonify({'error': 'Invalid line ID'}), 400
        
        success = sip_engine.hangup(line_id)
        
        if success:
            return jsonify({'status': 'idle'})
        else:
            return jsonify({'error': 'Failed to hangup'}), 500
            
    except Exception as e:
        logger.error(f"Error hanging up line {line_id}: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/lines/<int:line_id>/channel', methods=['POST'])
def api_set_audio_channel(line_id):
    """Set audio output channel for line"""
    try:
        if not 1 <= line_id <= 8:
            return jsonify({'error': 'Invalid line ID'}), 400
        
        data = request.get_json()
        channel = data.get('channel')
        
        if channel is None or not 0 <= channel <= 8:
            return jsonify({'error': 'Invalid channel (0-8)'}), 400
        
        line = sip_engine.get_line(line_id)
        line.set_audio_channel(channel)
        
        # Route audio through audio router
        if channel > 0:
            audio_router.route_line_to_channel(line_id, channel)
        else:
            audio_router.unroute_line(line_id)
        
        return jsonify({'status': 'success', 'channel': channel})
        
    except Exception as e:
        logger.error(f"Error setting audio channel for line {line_id}: {e}")
        return jsonify({'error': str(e)}), 500


# ============================================================================
# API ENDPOINTS - Configuration
# ============================================================================

@app.route('/api/config/sip', methods=['GET'])
def api_get_sip_config():
    """Get SIP configuration"""
    try:
        config_path = Path("config/sip_config.json")
        with open(config_path, 'r') as f:
            config = json.load(f)
        return jsonify(config)
    except Exception as e:
        logger.error(f"Error reading SIP config: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/config/sip', methods=['POST'])
def api_save_sip_config():
    """Save SIP configuration"""
    try:
        data = request.get_json()
        config_path = Path("config/sip_config.json")
        
        # Validate configuration
        if 'mode' not in data or 'sip_server' not in data:
            return jsonify({'error': 'Invalid configuration'}), 400
        
        # Save to file
        with open(config_path, 'w') as f:
            json.dump(data, f, indent=2)
        
        logger.info("SIP configuration saved")
        return jsonify({'status': 'saved', 'message': 'Configuration saved. Restart required.'})
        
    except Exception as e:
        logger.error(f"Error saving SIP config: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/config/network', methods=['GET'])
def api_get_network_config():
    """Get network configuration"""
    try:
        # Get current IP address
        result = subprocess.run(['hostname', '-I'], capture_output=True, text=True)
        current_ip = result.stdout.strip().split()[0] if result.stdout else "Unknown"
        
        # Check if static or DHCP
        route_result = subprocess.run(['ip', 'route', 'show', 'default'], 
                                     capture_output=True, text=True, timeout=2)
        is_static = 'proto static' in route_result.stdout
        
        mode = 'static' if is_static else 'dhcp'
        
        return jsonify({
            'mode': mode,
            'current_ip': current_ip,
            'ip_address': current_ip if is_static else '',
            'subnet_mask': '255.255.255.0',
            'gateway': '',
            'dns_server': '8.8.8.8'
        })
        
    except Exception as e:
        logger.error(f"Error reading network config: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/config/network', methods=['POST'])
def api_save_network_config():
    """Save network configuration and reboot"""
    try:
        data = request.get_json()
        mode = data.get('mode', 'dhcp')
        
        if mode == 'static':
            ip_address = data.get('ip_address')
            subnet_mask = data.get('subnet_mask', '255.255.255.0')
            gateway = data.get('gateway')
            dns_server = data.get('dns_server', '8.8.8.8')
            
            if not ip_address or not gateway:
                return jsonify({'error': 'IP address and gateway required'}), 400
            
            # Convert subnet to CIDR
            cidr_map = {
                '255.255.255.0': '24',
                '255.255.0.0': '16',
                '255.0.0.0': '8'
            }
            cidr = cidr_map.get(subnet_mask, '24')
            
            # Write network config
            config_content = f"""# PhoneSystem-Web Network Configuration
network:
  version: 2
  renderer: NetworkManager
  ethernets:
    eth0:
      dhcp4: false
      addresses:
        - {ip_address}/{cidr}
      routes:
        - to: default
          via: {gateway}
      nameservers:
        addresses:
          - {dns_server}
"""
            with open('/tmp/procomm_network.conf', 'w') as f:
                f.write(config_content)
            
            # Apply configuration using helper script
            script_path = os.path.expanduser("~/PhoneSystem-Web/scripts/update_network.sh")
            if os.path.exists(script_path):
                subprocess.run(['sudo', '-n', script_path], timeout=5)
                subprocess.Popen(['sudo', 'reboot'])
                return jsonify({'status': 'rebooting'})
            else:
                return jsonify({'error': 'Network script not found'}), 500
        
        else:  # DHCP mode
            config_content = """# PhoneSystem-Web Network Configuration
network:
  version: 2
  renderer: NetworkManager
  ethernets:
    eth0:
      dhcp4: true
"""
            with open('/tmp/procomm_network.conf', 'w') as f:
                f.write(config_content)
            
            # Apply configuration
            script_path = os.path.expanduser("~/PhoneSystem-Web/scripts/update_network.sh")
            if os.path.exists(script_path):
                subprocess.run(['sudo', '-n', script_path], timeout=5)
                subprocess.Popen(['sudo', 'reboot'])
                return jsonify({'status': 'rebooting'})
            else:
                return jsonify({'error': 'Network script not found'}), 500
        
    except Exception as e:
        logger.error(f"Error saving network config: {e}")
        return jsonify({'error': str(e)}), 500


# ============================================================================
# API ENDPOINTS - Audio
# ============================================================================

@app.route('/api/audio/test', methods=['POST'])
def api_start_test_tone():
    """Start test tone on specified channel"""
    try:
        data = request.get_json()
        channel = data.get('channel')
        
        if channel is None or not 1 <= channel <= 8:
            return jsonify({'error': 'Invalid channel (1-8)'}), 400
        
        audio_router.start_continuous_tone(channel)
        return jsonify({'status': 'playing', 'channel': channel})
        
    except Exception as e:
        logger.error(f"Error starting test tone: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/audio/test', methods=['DELETE'])
def api_stop_test_tone():
    """Stop test tone"""
    try:
        audio_router.stop_continuous_tone()
        return jsonify({'status': 'stopped'})
    except Exception as e:
        logger.error(f"Error stopping test tone: {e}")
        return jsonify({'error': str(e)}), 500


# ============================================================================
# API ENDPOINTS - System
# ============================================================================

@app.route('/api/system/status', methods=['GET'])
def api_system_status():
    """Get system health status"""
    try:
        return jsonify({
            'status': 'running',
            'sip_engine': 'running' if sip_engine else 'stopped',
            'audio_router': 'running' if audio_router and audio_router.is_running else 'stopped',
            'lines_registered': sum(1 for i in range(1, 9) if sip_engine.get_line(i).state != LineState.ERROR)
        })
    except Exception as e:
        logger.error(f"Error getting system status: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/system/restart', methods=['POST'])
def api_restart_system():
    """Restart phone system service"""
    try:
        # Restart systemd service
        subprocess.run(['sudo', 'systemctl', 'restart', 'phonesystem'], timeout=5)
        return jsonify({'status': 'restarting'})
    except Exception as e:
        logger.error(f"Error restarting system: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/system/reboot', methods=['POST'])
def api_reboot_pi():
    """Reboot Raspberry Pi"""
    try:
        subprocess.Popen(['sudo', 'reboot'])
        return jsonify({'status': 'rebooting'})
    except Exception as e:
        logger.error(f"Error rebooting: {e}")
        return jsonify({'error': str(e)}), 500


# ============================================================================
# WEBSOCKET EVENTS
# ============================================================================

@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    logger.info(f"Client connected: {request.sid}")
    emit('connected', {'status': 'connected'})


@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    logger.info(f"Client disconnected: {request.sid}")


@socketio.on('subscribe')
def handle_subscribe(data):
    """Subscribe to line updates"""
    lines = data.get('lines', [])
    logger.info(f"Client {request.sid} subscribed to lines: {lines}")
    # Client is now subscribed - they'll receive all line_status events


# ============================================================================
# MAIN
# ============================================================================

if __name__ == '__main__':
    # Initialize phone system
    if not init_phone_system():
        logger.error("Failed to initialize phone system - exiting")
        exit(1)
    
    # Run Flask app with SocketIO
    logger.info("Starting web server on http://0.0.0.0:5000")
    socketio.run(app, host='0.0.0.0', port=5000, debug=False, allow_unsafe_werkzeug=True)
