// Character counter
const promptTextarea = document.getElementById('prompt');
const charCount = document.getElementById('charCount');

promptTextarea.addEventListener('input', () => {
    charCount.textContent = promptTextarea.value.length;
});

// Form submission
const meetingForm = document.getElementById('meetingForm');
const submitBtn = document.getElementById('submitBtn');
const resultDiv = document.getElementById('result');
const errorDiv = document.getElementById('error');

meetingForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const prompt = promptTextarea.value.trim();
    
    if (!prompt) {
        showError('Please enter meeting details');
        return;
    }
    
    // Show loading state
    submitBtn.classList.add('loading');
    submitBtn.disabled = true;
    hideResults();
    
    try {
        const response = await fetch('/schedule-meeting', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ prompt })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showSuccess(data);
        } else {
            showError(data.detail || 'Failed to schedule meeting');
        }
    } catch (error) {
        showError('Network error. Please check your connection and try again.');
        console.error('Error:', error);
    } finally {
        submitBtn.classList.remove('loading');
        submitBtn.disabled = false;
    }
});

function showSuccess(data) {
    hideResults();
    
    const meetingDetails = data.meeting_details;
    const eventLink = data.event_link;
    
    // Format the meeting info
    const meetingInfoHTML = `
        <div class="meeting-info-item">
            <span class="meeting-info-label">📋 Title:</span>
            <span class="meeting-info-value">${meetingDetails.title}</span>
        </div>
        <div class="meeting-info-item">
            <span class="meeting-info-label">👥 Participants:</span>
            <span class="meeting-info-value">${meetingDetails.participants.join(', ')}</span>
        </div>
        <div class="meeting-info-item">
            <span class="meeting-info-label">🕒 Start Time:</span>
            <span class="meeting-info-value">${formatDateTime(meetingDetails.start_time)}</span>
        </div>
        <div class="meeting-info-item">
            <span class="meeting-info-label">⏱️ Duration:</span>
            <span class="meeting-info-value">${meetingDetails.duration_minutes} minutes</span>
        </div>
        ${meetingDetails.agenda ? `
        <div class="meeting-info-item">
            <span class="meeting-info-label">📝 Agenda:</span>
            <span class="meeting-info-value">${meetingDetails.agenda}</span>
        </div>
        ` : ''}
    `;
    
    document.getElementById('meetingInfo').innerHTML = meetingInfoHTML;
    document.getElementById('eventLink').href = eventLink;
    
    resultDiv.classList.remove('hidden');
    resultDiv.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

function showError(message) {
    hideResults();
    
    document.getElementById('errorMessage').textContent = message;
    errorDiv.classList.remove('hidden');
    errorDiv.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

function hideResults() {
    resultDiv.classList.add('hidden');
    errorDiv.classList.add('hidden');
}

function resetForm() {
    meetingForm.reset();
    charCount.textContent = '0';
    hideResults();
    promptTextarea.focus();
}

function formatDateTime(isoString) {
    const date = new Date(isoString);
    const options = {
        weekday: 'long',
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
        timeZoneName: 'short'
    };
    return date.toLocaleString('en-US', options);
}

function fillExample(element) {
    const exampleText = element.querySelector('p').textContent;
    promptTextarea.value = exampleText;
    charCount.textContent = exampleText.length;
    promptTextarea.focus();
    
    // Smooth scroll to form
    meetingForm.scrollIntoView({ behavior: 'smooth', block: 'center' });
    
    // Add a highlight effect
    promptTextarea.style.background = '#fff9e6';
    setTimeout(() => {
        promptTextarea.style.background = '';
    }, 1000);
}

// Add enter key support (Ctrl+Enter to submit)
promptTextarea.addEventListener('keydown', (e) => {
    if (e.ctrlKey && e.key === 'Enter') {
        meetingForm.dispatchEvent(new Event('submit'));
    }
});
