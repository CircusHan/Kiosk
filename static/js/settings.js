document.addEventListener('DOMContentLoaded', () => {
    const settingsForm = document.getElementById('settings-form');
    const messageElement = document.getElementById('message');

    if (settingsForm) {
        settingsForm.addEventListener('submit', async (event) => {
            event.preventDefault();
            const apiKey = document.getElementById('gemini-api-key').value;
            messageElement.textContent = ''; // Clear previous messages

            try {
                const response = await fetch('/settings', { // Matches the FastAPI route
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/x-www-form-urlencoded', // FastAPI Form expects this
                    },
                    body: new URLSearchParams({
                        'gemini_api_key': apiKey
                    })
                });

                const result = await response.json();

                if (response.ok) {
                    messageElement.textContent = result.message || 'API Key saved successfully!';
                    messageElement.style.color = 'green';
                } else {
                    messageElement.textContent = result.message || 'Error saving API Key.';
                    messageElement.style.color = 'red';
                }
            } catch (error) {
                console.error('Error saving API key:', error);
                messageElement.textContent = 'An unexpected error occurred.';
                messageElement.style.color = 'red';
            }
        });
    }
});
