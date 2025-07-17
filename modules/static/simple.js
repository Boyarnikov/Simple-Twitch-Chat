let last_id_requested = -1;

function addMessagesToPage(messages) {
    const chatContainer = document.querySelector('.chat-container');

    messages.forEach(msg => {
        last_id_requested = Math.max(last_id_requested, msg.id);

        const messageEl = document.createElement('div');
        messageEl.className = 'message';
        messageEl.textContent = `${msg.username}: ${msg.text}`;

        // Auto-remove after animation completes
        messageEl.addEventListener('animationend', (e) => {
            if (e.animationName === 'fadeOut') {
                messageEl.remove();
            }
        });

        chatContainer.appendChild(messageEl);
    });

    // Scroll to bottom to show new messages
    scrollToBottom();
}

async function fetchUpdates() {
    try {
        const response = await fetch('/data', {
            method: 'FETCH',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({from_id: last_id_requested})
        });
        const data = await response.json();
        if (data.reset_index !== undefined) last_id_requested = data.reset_index;
        if (data.data?.length > 0) addMessagesToPage(data.data);
    } catch (error) {
        console.error('Error:', error);
    }
}


function scrollToBottom() {
    const chatContainer = document.querySelector('.chat-container');
    chatContainer.scrollTop = chatContainer.scrollHeight;
}


document.addEventListener('DOMContentLoaded', () => {
    fetchUpdates();
    setInterval(fetchUpdates, 1500);
});