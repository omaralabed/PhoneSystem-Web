/**
 * Main Application Logic
 * Handles line widgets, UI updates, and user interactions
 */

// State
let linesState = {};
let testToneActive = false;

// Initialize application
document.addEventListener('DOMContentLoaded', () => {
    console.log('PhoneSystem-Web initialized');
    
    // Connect to WebSocket
    wsManager.connect();
    
    // Set up WebSocket callbacks
    wsManager.on('onConnect', () => {
        console.log('Connected to server');
        loadAllLines();
    });
    
    wsManager.on('onLineStatus', (data) => {
        updateLineUI(data);
    });
    
    // Set up UI event listeners
    setupEventListeners();
    
    // Load initial line status
    loadAllLines();
});

// Load all line statuses from API
function loadAllLines() {
    fetch('/api/lines')
        .then(response => response.json())
        .then(lines => {
            lines.forEach(line => {
                linesState[line.line_id] = line;
                updateLineUI(line);
            });
        })
        .catch(error => {
            console.error('Error loading lines:', error);
        });
}

// Update line UI based on status data
function updateLineUI(data) {
    const lineId = data.line_id;
    const lineWidget = document.querySelector(`.line-widget[data-line-id="${lineId}"]`);
    
    if (!lineWidget) return;
    
    // Update state
    linesState[lineId] = { ...linesState[lineId], ...data };
    
    // Update status text
    const statusEl = lineWidget.querySelector('.line-status');
    const actionBtn = lineWidget.querySelector('.action-btn');
    
    switch (data.state) {
        case 'idle':
            statusEl.textContent = 'Available';
            statusEl.className = 'line-status';
            actionBtn.textContent = '📞 DIAL';
            actionBtn.className = 'btn btn-dial action-btn';
            break;
        
        case 'dialing':
            statusEl.textContent = `Dialing ${data.phone_number}...`;
            statusEl.className = 'line-status active';
            actionBtn.textContent = '🔴 HANGUP';
            actionBtn.className = 'btn btn-hangup action-btn';
            break;
        
        case 'ringing':
            statusEl.textContent = `Ringing ${data.phone_number}...`;
            statusEl.className = 'line-status ringing';
            actionBtn.textContent = '🔴 HANGUP';
            actionBtn.className = 'btn btn-hangup action-btn';
            break;
        
        case 'connected':
            const duration = formatDuration(data.duration || 0);
            statusEl.textContent = `Active: ${data.phone_number} (${duration})`;
            statusEl.className = 'line-status active';
            actionBtn.textContent = '🔴 HANGUP';
            actionBtn.className = 'btn btn-hangup action-btn';
            break;
        
        default:
            statusEl.textContent = data.state;
            statusEl.className = 'line-status';
    }
    
    // Update audio channel
    if (data.audio_channel !== undefined) {
        const channelPicker = lineWidget.querySelector('.channel-picker');
        channelPicker.value = data.audio_channel;
    }
}

// Format call duration
function formatDuration(seconds) {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
}

// Set up all event listeners
function setupEventListeners() {
    // Action buttons (DIAL/HANGUP)
    document.querySelectorAll('.action-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            const lineId = parseInt(e.target.dataset.lineId);
            const state = linesState[lineId]?.state || 'idle';
            
            if (state === 'idle') {
                // Show dial pad
                showDialPad(lineId);
            } else {
                // Hangup
                hangupLine(lineId);
            }
        });
    });
    
    // Channel pickers
    document.querySelectorAll('.channel-picker').forEach(select => {
        select.addEventListener('change', (e) => {
            const lineId = parseInt(e.target.dataset.lineId);
            const channel = parseInt(e.target.value);
            setAudioChannel(lineId, channel);
        });
    });
    
    // Test tone button
    const testBtn = document.getElementById('hold-test-btn');
    if (testBtn) {
        testBtn.addEventListener('mousedown', startTestTone);
        testBtn.addEventListener('mouseup', stopTestTone);
        testBtn.addEventListener('mouseleave', stopTestTone);
        testBtn.addEventListener('touchstart', startTestTone);
        testBtn.addEventListener('touchend', stopTestTone);
    }
    
    // Settings button
    const settingsBtn = document.getElementById('settings-btn');
    if (settingsBtn) {
        settingsBtn.addEventListener('click', showSettings);
    }
}

// Hangup line
function hangupLine(lineId) {
    if (!confirm(`Hang up Line ${lineId}?`)) {
        return;
    }
    
    fetch(`/api/lines/${lineId}/hangup`, {
        method: 'POST'
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            alert('Error hanging up: ' + data.error);
        }
    })
    .catch(error => {
        console.error('Error hanging up:', error);
        alert('Error hanging up line');
    });
}

// Set audio channel for line
function setAudioChannel(lineId, channel) {
    fetch(`/api/lines/${lineId}/channel`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ channel })
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            console.error('Error setting channel:', data.error);
        }
    })
    .catch(error => {
        console.error('Error setting channel:', error);
    });
}

// Start test tone
function startTestTone() {
    if (testToneActive) return;
    
    const channel = parseInt(document.getElementById('test-channel').value);
    
    fetch('/api/audio/test', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ channel })
    })
    .then(response => response.json())
    .then(data => {
        if (!data.error) {
            testToneActive = true;
        }
    })
    .catch(error => {
        console.error('Error starting test tone:', error);
    });
}

// Stop test tone
function stopTestTone() {
    if (!testToneActive) return;
    
    fetch('/api/audio/test', {
        method: 'DELETE'
    })
    .then(response => response.json())
    .then(data => {
        testToneActive = false;
    })
    .catch(error => {
        console.error('Error stopping test tone:', error);
    });
}

// Show settings menu
function showSettings() {
    document.getElementById('settings-modal').classList.add('active');
}

// Close settings menu
function closeSettings() {
    document.getElementById('settings-modal').classList.remove('active');
}

// Reboot system
function rebootSystem() {
    if (!confirm('Reboot the system?')) {
        return;
    }
    
    fetch('/api/system/reboot', {
        method: 'POST'
    })
    .then(response => response.json())
    .then(data => {
        alert('System is rebooting...');
        closeSettings();
    })
    .catch(error => {
        console.error('Error rebooting:', error);
        alert('Error rebooting system');
    });
}

// Update call durations every second
setInterval(() => {
    Object.keys(linesState).forEach(lineId => {
        const line = linesState[lineId];
        if (line.state === 'connected' && line.duration !== undefined) {
            line.duration++;
            updateLineUI(line);
        }
    });
}, 1000);
