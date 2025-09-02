// Application state variables
let currentEmailId = null;
let emails = [];

// Main functions
async function connectGmail() {
    const connectBtn = document.getElementById('connectBtn');
    const originalText = connectBtn.textContent;

    try {
        connectBtn.textContent = 'Connecting...';
        connectBtn.disabled = true;

        const response = await fetch('/auth/url');
        const data = await response.json();

        console.log('Auth URL response:', data);

        if (data.auth_url) {
            connectBtn.textContent = 'Opening OAuth...';
            window.open(data.auth_url, '_blank');
            // Poll for connection status
            pollConnectionStatus();
        } else {
            alert(`Please set up Google credentials first.

Steps:
1. Run: python3 setup_google_auth.py
2. Follow the instructions to download credentials.json`);
            connectBtn.textContent = originalText;
            connectBtn.disabled = false;
        }
    } catch (error) {
        console.error('Connection error:', error);
        alert('Error connecting to Gmail: ' + error.message);
        connectBtn.textContent = originalText;
        connectBtn.disabled = false;
    }
}

async function pollConnectionStatus() {
    let attempts = 0;
    const maxAttempts = 30; // Poll for 1 minute

    const interval = setInterval(async () => {
        attempts++;

        try {
            const response = await fetch('/status');
            const data = await response.json();

            if (data.connected) {
                clearInterval(interval);
                updateConnectionStatus(true);
                refreshEmails();
            } else if (attempts >= maxAttempts) {
                // Timeout - re-enable connect button
                clearInterval(interval);
                const connectBtn = document.getElementById('connectBtn');
                connectBtn.textContent = 'Connect Gmail';
                connectBtn.disabled = false;
                alert('Connection timeout. Please try again.');
            }
        } catch (error) {
            console.error('Error checking status:', error);
            if (attempts >= maxAttempts) {
                clearInterval(interval);
                const connectBtn = document.getElementById('connectBtn');
                connectBtn.textContent = 'Connect Gmail';
                connectBtn.disabled = false;
            }
        }
    }, 2000);
}

function updateConnectionStatus(connected) {
    const status = document.getElementById('status');
    const connectBtn = document.getElementById('connectBtn');
    const refreshBtn = document.getElementById('refreshBtn');

    if (connected) {
        status.textContent = 'Connected ✓';
        status.className = 'status connected';
        connectBtn.disabled = true;
        refreshBtn.disabled = false;
    } else {
        status.textContent = 'Not Connected';
        status.className = 'status disconnected';
        connectBtn.disabled = false;
        refreshBtn.disabled = true;
    }
}

async function refreshEmails() {
    document.getElementById('emailList').innerHTML = '<div class="loading">Loading emails...</div>';

    try {
        const response = await fetch('/emails');
        const data = await response.json();
        
        // Handle new API response format
        if (data.error) {
            document.getElementById('emailList').innerHTML = `<div class="loading">Error: ${data.error}</div>`;
            return;
        }
        
        emails = Array.isArray(data) ? data : data.emails || [];
        displayEmails(emails);
        updateSummary(emails);
        loadOverallSummary(); // Load the comprehensive summary
    } catch (error) {
        console.error('Error refreshing emails:', error);
        document.getElementById('emailList').innerHTML = '<div class="loading">Error loading emails</div>';
    }
}

function displayEmails(emails) {
    const emailList = document.getElementById('emailList');

    if (emails.length === 0) {
        emailList.innerHTML = '<div class="loading">No emails found</div>';
        return;
    }

    // Sort emails: Tasks first, then by priority
    const sortedEmails = [...emails].sort((a, b) => {
        // First priority: emails with tasks
        if (a.has_tasks && !b.has_tasks) return -1;
        if (!a.has_tasks && b.has_tasks) return 1;

        // Second priority: priority score
        return b.priority_score - a.priority_score;
    });

    emailList.innerHTML = sortedEmails.map((email, index) => {
        const priorityClass = email.priority_score > 0.7 ? 'high-priority' :
            email.priority_score > 0.5 ? 'medium-priority' : 'low-priority';

        // Format date
        const emailDate = new Date(email.date || Date.now());
        const timeStr = emailDate.toLocaleDateString() + ' ' + emailDate.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

        // Extract sender name (remove email part)
        const senderName = email.sender.includes('<') ?
            email.sender.split('<')[0].trim().replaceAll('"', '') :
            email.sender.split('@')[0];

        // Get priority emoji
        const priorityEmoji = email.priority_score > 0.7 ? '🔴' :
            email.priority_score > 0.5 ? '🟡' : '🟢';

        return `
            <div class="email-item ${priorityClass} ${email.has_tasks ? 'has-tasks' : ''}" data-email-id="${email.id}" data-index="${index}">
                <div class="email-compact" onclick="toggleEmailExpansion('${email.id}', ${index})">
                    <div class="email-header">
                        <div class="email-sender">
                            <div class="sender-info">
                                <strong>${senderName.substring(0, 25)}</strong>
                                <div class="sender-indicators">
                                    ${email.has_tasks ? '<span class="task-indicator" title="Contains tasks">📅</span>' : ''}
                                    ${email.is_important ? '<span class="important-indicator" title="Important">⭐</span>' : ''}
                                    <span class="priority-indicator" title="Priority: ${email.priority_score.toFixed(2)}">${priorityEmoji}</span>
                                </div>
                            </div>
                        </div>
                        <div class="email-actions">
                            <div class="email-time">${timeStr}</div>
                            <div class="expand-arrow">▼</div>
                        </div>
                    </div>
                    <div class="email-subject">${email.subject}</div>
                    <div class="email-preview">${email.body.substring(0, 120)}${email.body.length > 120 ? '...' : ''}</div>
                    <div class="email-footer">
                        <div class="email-labels">
                            ${email.labels.map(label => `<span class="label">${label}</span>`).join('')}
                            ${email.has_tasks ? '<span class="label task-label">📅 Tasks</span>' : ''}
                        </div>
                        <div class="priority-score">Score: ${email.priority_score.toFixed(2)}</div>
                    </div>
                </div>
                
                <div class="email-expanded" id="expanded-${email.id}" style="display: none;">
                    <div class="email-full-content">
                        <div class="email-meta-info">
                            <div class="meta-row">
                                <span class="meta-label">From:</span>
                                <span class="meta-value">${email.sender}</span>
                            </div>
                            <div class="meta-row">
                                <span class="meta-label">Subject:</span>
                                <span class="meta-value">${email.subject}</span>
                            </div>
                            <div class="meta-row">
                                <span class="meta-label">Date:</span>
                                <span class="meta-value">${emailDate.toLocaleDateString()} at ${emailDate.toLocaleTimeString()}</span>
                            </div>
                            <div class="meta-row">
                                <span class="meta-label">Priority:</span>
                                <span class="meta-value">${priorityEmoji} ${email.priority_score.toFixed(2)}/1.0 ${email.is_important ? '(Important)' : ''}</span>
                            </div>
                            <div class="meta-row">
                                <span class="meta-label">Labels:</span>
                                <span class="meta-value">
                                    ${email.labels.length > 0 ?
                email.labels.map(label => `<span class="inline-label">${label}</span>`).join(' ') :
                'No labels'
            }
                                </span>
                            </div>
                        </div>
                        
                        <div class="email-content-section">
                            <div class="content-header">
                                <span class="content-label">📄 Email Content</span>
                                ${email.has_tasks ? '<span class="task-detected">📅 Tasks Detected</span>' : ''}
                            </div>
                            <div class="email-body-full">${email.body}</div>
                        </div>
                        
                        <div class="email-actions-section">
                            <button class="action-btn ${email.has_tasks ? 'primary' : 'disabled'}" 
                                    onclick="addToCalendarFromExpanded('${email.id}')"
                                    ${!email.has_tasks ? 'disabled' : ''}>
                                ${email.has_tasks ? '📅 Add to Calendar' : '📅 No Tasks Found'}
                            </button>
                            <button class="action-btn secondary" onclick="selectEmailInSidebar('${email.id}', ${index})">
                                🤖 View AI Summary
                            </button>
                            <button class="action-btn secondary" onclick="copyEmailContent('${email.id}')">
                                📋 Copy Content
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }).join('');
}

function toggleEmailExpansion(emailId, index) {
    const expandedDiv = document.getElementById(`expanded-${emailId}`);
    const emailItem = document.querySelector(`[data-email-id="${emailId}"]`);
    const arrow = emailItem.querySelector('.expand-arrow');

    if (expandedDiv.style.display === 'none') {
        // Close all other expanded emails
        document.querySelectorAll('.email-expanded').forEach(div => {
            div.style.display = 'none';
        });
        document.querySelectorAll('.expand-arrow').forEach(arr => {
            arr.textContent = '▼';
            arr.style.transform = 'rotate(0deg)';
        });
        document.querySelectorAll('.email-item').forEach(item => {
            item.classList.remove('expanded');
        });

        // Expand this email
        expandedDiv.style.display = 'block';
        arrow.textContent = '▲';
        arrow.style.transform = 'rotate(180deg)';
        emailItem.classList.add('expanded');

        // Smooth scroll to the expanded email
        setTimeout(() => {
            emailItem.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
        }, 100);
    } else {
        // Collapse this email
        expandedDiv.style.display = 'none';
        arrow.textContent = '▼';
        arrow.style.transform = 'rotate(0deg)';
        emailItem.classList.remove('expanded');
    }
}

function selectEmailInSidebar(emailId, index) {
    currentEmailId = emailId;
    const email = emails.find(e => e.id === emailId);

    // Remove previous selection
    document.querySelectorAll('.email-item').forEach(item => {
        item.classList.remove('selected');
    });

    // Add selection to current item
    document.querySelector(`[data-email-id="${emailId}"]`)?.classList.add('selected');

    if (email) {
        // Load AI summary
        loadEmailSummary(emailId);

        // Format the email details nicely
        const emailDate = new Date(email.date || Date.now());
        const formattedDate = emailDate.toLocaleDateString() + ' at ' + emailDate.toLocaleTimeString();

        const details = `
            <div class="email-detail-header">
                <h4>${email.subject}</h4>
                <div class="email-meta">
                    <div><strong>From:</strong> ${email.sender}</div>
                    <div><strong>Date:</strong> ${formattedDate}</div>
                    <div><strong>Priority Score:</strong> ${email.priority_score.toFixed(2)}/1.0</div>
                    <div><strong>Important:</strong> ${email.is_important ? '⭐ Yes' : 'No'}</div>
                    <div><strong>Contains Tasks:</strong> ${email.has_tasks ? '📅 Yes' : 'No'}</div>
                </div>
            </div>
            
            <div class="email-labels-section">
                <strong>Labels:</strong>
                ${email.labels.length > 0 ?
                email.labels.map(label => `<span class="label">${label}</span>`).join(' ') :
                '<span class="no-labels">No labels</span>'
            }
            </div>
            
            <div class="email-content">
                <strong>Content:</strong>
                <div class="email-body">${email.body}</div>
            </div>
        `;

        document.getElementById('emailDetails').innerHTML = details;

        // Show summary actions
        document.getElementById('summaryActions').style.display = 'flex';

        // Update calendar button
        const calendarBtn = document.getElementById('addToCalendar');
        calendarBtn.disabled = !email.has_tasks;
        if (email.has_tasks) {
            calendarBtn.textContent = '📅 Add Tasks to Calendar';
            calendarBtn.className = 'btn primary';
        } else {
            calendarBtn.textContent = '📅 No Tasks Detected';
            calendarBtn.className = 'btn disabled';
        }
    }
}

async function loadEmailSummary(emailId) {
    const summaryContainer = document.getElementById('emailSummary');

    // Show loading state
    summaryContainer.innerHTML = `
        <div class="summary-loading">
            <div class="loading-spinner"></div>
            <h4>🤖 Generating Summary...</h4>
            <p>Creating a simple summary of this email</p>
        </div>
    `;

    try {
        const response = await fetch(`/email/summary/${emailId}`);
        const data = await response.json();

        if (data.error) {
            throw new Error(data.error);
        }

        // Count words in summary
        const wordCount = data.summary.split(' ').length;
        
        // Display the simple summary
        summaryContainer.innerHTML = `
            <div class="ai-summary">
                <div class="summary-header">
                    <span class="ai-badge">${data.generated_with_ai ? '🤖 AI Summary' : '📝 Quick Summary'}</span>
                    <span class="word-count">${wordCount} words</span>
                </div>
                <div class="summary-content simple">
                    ${data.summary.replace(/\n/g, '<br>')}
                </div>
                <div class="summary-footer">
                    <small>📄 ${data.generated_with_ai ? 'AI-powered' : 'Smart'} summary under 150 words</small>
                </div>
            </div>
        `;

        // Update AI status
        document.getElementById('aiStatus').innerHTML = `
            <span class="ai-indicator success">✅ Summary Ready</span>
        `;

    } catch (error) {
        console.error('Error loading summary:', error);
        summaryContainer.innerHTML = `
            <div class="summary-error">
                <div class="error-icon">⚠️</div>
                <h4>Summary Unavailable</h4>
                <p>Unable to generate summary for this email. Please try again.</p>
            </div>
        `;

        document.getElementById('aiStatus').innerHTML = `
            <span class="ai-indicator error">❌ Summary Failed</span>
        `;
    }
}

async function regenerateSummary() {
    if (currentEmailId) {
        await loadEmailSummary(currentEmailId);
    }
}

function addToCalendarFromExpanded(emailId) {
    currentEmailId = emailId;
    addToCalendar();
}

function copyEmailContent(emailId) {
    const email = emails.find(e => e.id === emailId);
    if (email) {
        const content = `Subject: ${email.subject}\nFrom: ${email.sender}\n\n${email.body}`;
        navigator.clipboard.writeText(content).then(() => {
            // Show temporary success message
            const btn = event.target;
            const originalText = btn.textContent;
            btn.textContent = '✅ Copied!';
            btn.style.background = '#28a745';
            setTimeout(() => {
                btn.textContent = originalText;
                btn.style.background = '';
            }, 2000);
        });
    }
}

function updateSummary(emails) {
    const total = emails.length;
    const important = emails.filter(e => e.is_important).length;
    const withTasks = emails.filter(e => e.has_tasks).length;
    const highPriority = emails.filter(e => e.priority_score > 0.7).length;

    document.getElementById('summary').innerHTML = `
        <div class="summary-item">📧 Total Emails: <strong>${total}</strong></div>
        <div class="summary-item priority">🔴 High Priority: <strong>${highPriority}</strong></div>
        <div class="summary-item tasks">📅 With Tasks: <strong>${withTasks}</strong></div>
        <div class="summary-item">⭐ Important: <strong>${important}</strong></div>
    `;

    // Update labels with better formatting
    const labelCounts = {};
    emails.forEach(email => {
        email.labels.forEach(label => {
            labelCounts[label] = (labelCounts[label] || 0) + 1;
        });
    });

    const sortedLabels = Object.entries(labelCounts)
        .sort(([, a], [, b]) => b - a) // Sort by count descending
        .slice(0, 8); // Show top 8 labels

    const labelsHtml = sortedLabels.length > 0 ?
        sortedLabels.map(([label, count]) =>
            `<div class="label-count">
                <span class="label-name">${label}</span>
                <span class="label-number">${count}</span>
            </div>`
        ).join('') :
        '<div class="no-labels">No labels found</div>';

    document.getElementById('labels').innerHTML = labelsHtml;
}

async function loadOverallSummary() {
    const summaryContainer = document.getElementById('overallSummary');

    // Show loading state
    summaryContainer.innerHTML = `
        <div class="briefing-loading">
            <div class="briefing-spinner"></div>
            <div>Generating daily briefing...</div>
        </div>
    `;

    try {
        const response = await fetch('/summary/overall');
        const data = await response.json();

        if (data.error) {
            throw new Error(data.error);
        }

        // Display the overall summary
        summaryContainer.innerHTML = `
            <div class="briefing-header">
                <span class="briefing-badge">${data.generated_with_ai ? '🤖 AI Briefing' : '📊 Smart Analysis'}</span>
            </div>
            <div class="briefing-content">
                ${data.summary.replace(/\n/g, '<br>').replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')}
            </div>
        `;

    } catch (error) {
        console.error('Error loading overall summary:', error);
        summaryContainer.innerHTML = `
            <div class="summary-placeholder">
                <div class="placeholder-text">Unable to generate briefing. Please try refreshing.</div>
            </div>
        `;
    }
}

async function addToCalendar() {
    if (!currentEmailId) return;

    try {
        const response = await fetch(`/calendar/add/${currentEmailId}`, { method: 'POST' });
        const result = await response.json();

        if (result.success) {
            alert('Task added to calendar successfully!');
        } else {
            alert('Failed to add to calendar');
        }
    } catch (error) {
        alert('Error adding to calendar: ' + error.message);
    }
}

// Initialize the app
document.addEventListener('DOMContentLoaded', function () {
    // Check initial connection status
    fetch('/status').then(response => response.json()).then(data => {
        updateConnectionStatus(data.connected);
        if (data.connected) {
            refreshEmails();
        }
    }).catch(error => {
        console.error('Error checking initial status:', error);
        updateConnectionStatus(false);
    });

    // Auto-refresh every 5 minutes
    setInterval(() => {
        if (document.getElementById('refreshBtn').disabled === false) {
            refreshEmails();
        }
    }, 300000);
});