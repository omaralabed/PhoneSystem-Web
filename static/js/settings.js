/**
 * Settings Page Functionality
 * Handles SIP settings loading and saving
 */

// Load SIP configuration
function loadSIPConfig() {
    fetch('/api/config/sip')
        .then(response => response.json())
        .then(config => {
            // Global settings
            document.getElementById('sip-server').value = config.sip_server || '';
            document.getElementById('sip-port').value = config.sip_port || 5060;
            document.getElementById('transport').value = config.transport || 'UDP';
            
            // Line settings
            if (config.lines && Array.isArray(config.lines)) {
                config.lines.forEach(line => {
                    const lineId = line.line_id;
                    document.getElementById(`line-${lineId}-username`).value = line.username || '';
                    document.getElementById(`line-${lineId}-password`).value = line.password || '';
                    document.getElementById(`line-${lineId}-callerid-name`).value = line.caller_id_name || '';
                    document.getElementById(`line-${lineId}-callerid-number`).value = line.caller_id_number || '';
                    
                    // Update summary
                    updateLineSummary(lineId);
                });
            }
        })
        .catch(error => {
            console.error('Error loading SIP config:', error);
            alert('Error loading SIP configuration');
        });
}

// Update line summary text
function updateLineSummary(lineId) {
    const username = document.getElementById(`line-${lineId}-username`).value;
    const summary = document.getElementById(`line-${lineId}-summary`);
    
    if (username) {
        summary.textContent = username;
        summary.style.color = 'var(--accent-cyan)';
    } else {
        summary.textContent = 'Not configured';
        summary.style.color = 'var(--text-muted)';
    }
}

// Toggle line section expand/collapse
function toggleLineSection(lineId) {
    const section = document.getElementById(`line-section-${lineId}`);
    section.classList.toggle('expanded');
}

// Save SIP settings
function saveSIPSettings() {
    // Gather global settings
    const config = {
        mode: 'multi_account',
        sip_server: document.getElementById('sip-server').value,
        sip_port: parseInt(document.getElementById('sip-port').value) || 5060,
        transport: document.getElementById('transport').value,
        num_lines: 8,
        lines: []
    };
    
    // Gather line settings
    for (let lineId = 1; lineId <= 8; lineId++) {
        config.lines.push({
            line_id: lineId,
            username: document.getElementById(`line-${lineId}-username`).value || '',
            password: document.getElementById(`line-${lineId}-password`).value || '',
            caller_id_name: document.getElementById(`line-${lineId}-callerid-name`).value || `Line ${lineId}`,
            caller_id_number: document.getElementById(`line-${lineId}-callerid-number`).value || ''
        });
    }
    
    // Validate
    if (!config.sip_server) {
        alert('Please enter SIP server');
        return;
    }
    
    // Confirm
    if (!confirm('Save SIP settings? System will restart to apply changes.')) {
        return;
    }
    
    // Save
    fetch('/api/config/sip', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(config)
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            alert('Error saving: ' + data.error);
        } else {
            alert('SIP settings saved! System will restart.');
            // Redirect to home after a delay
            setTimeout(() => {
                window.location.href = '/';
            }, 2000);
        }
    })
    .catch(error => {
        console.error('Error saving SIP config:', error);
        alert('Error saving SIP configuration');
    });
}

// Auto-update summaries on input change
document.addEventListener('DOMContentLoaded', () => {
    // Load config when page loads
    if (document.getElementById('sip-server')) {
        loadSIPConfig();
        
        // Add input listeners for summary updates
        for (let lineId = 1; lineId <= 8; lineId++) {
            const usernameInput = document.getElementById(`line-${lineId}-username`);
            if (usernameInput) {
                usernameInput.addEventListener('input', () => updateLineSummary(lineId));
            }
        }
    }
});
