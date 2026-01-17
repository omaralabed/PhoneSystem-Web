/**
 * Dial Pad Functionality
 * Manages phone number input and dialing
 */

let currentLineForDial = null;
let dialNumber = '';
let recentNumbers = [];

// Load recent numbers from localStorage
function loadRecentNumbers() {
    const stored = localStorage.getItem('recentNumbers');
    if (stored) {
        try {
            recentNumbers = JSON.parse(stored);
        } catch (e) {
            recentNumbers = [];
        }
    }
}

// Save recent numbers to localStorage
function saveRecentNumbers() {
    localStorage.setItem('recentNumbers', JSON.stringify(recentNumbers.slice(0, 20)));
}

// Add number to recents
function addToRecents(number) {
    // Remove if already exists
    recentNumbers = recentNumbers.filter(n => n !== number);
    // Add to front
    recentNumbers.unshift(number);
    // Keep only last 20
    recentNumbers = recentNumbers.slice(0, 20);
    saveRecentNumbers();
}

// Show dial pad for specific line
function showDialPad(lineId) {
    currentLineForDial = lineId;
    dialNumber = '';
    document.getElementById('dial-line-number').textContent = lineId;
    document.getElementById('dial-display').value = '';
    document.getElementById('dial-modal').classList.add('active');
}

// Close dial pad
function closeDialPad() {
    document.getElementById('dial-modal').classList.remove('active');
    currentLineForDial = null;
    dialNumber = '';
}

// Dial pad button press
function dialPadPress(digit) {
    dialNumber += digit;
    document.getElementById('dial-display').value = dialNumber;
}

// Backspace
function dialPadBackspace() {
    dialNumber = dialNumber.slice(0, -1);
    document.getElementById('dial-display').value = dialNumber;
}

// Clear
function dialPadClear() {
    dialNumber = '';
    document.getElementById('dial-display').value = '';
}

// Show recents
function showRecents() {
    if (recentNumbers.length === 0) {
        alert('No recent numbers');
        return;
    }
    
    const number = prompt('Recent numbers:\n\n' + recentNumbers.join('\n') + '\n\nEnter number to dial:');
    if (number) {
        dialNumber = number;
        document.getElementById('dial-display').value = dialNumber;
    }
}

// Make call
function makeCall() {
    if (!dialNumber || !currentLineForDial) {
        alert('Please enter a phone number');
        return;
    }
    
    // Add to recents
    addToRecents(dialNumber);
    
    // Call API
    fetch(`/api/lines/${currentLineForDial}/dial`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            phone_number: dialNumber
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            alert('Failed to dial: ' + data.error);
        } else {
            console.log('Dialing:', data);
            closeDialPad();
        }
    })
    .catch(error => {
        console.error('Error dialing:', error);
        alert('Error dialing: ' + error);
    });
}

// Initialize on load
loadRecentNumbers();
