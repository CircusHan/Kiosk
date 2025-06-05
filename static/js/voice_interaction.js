document.addEventListener('DOMContentLoaded', () => {
    const toggleMicBtn = document.getElementById('toggle-mic-btn');
    const statusDiv = document.getElementById('status');
    const userInputP = document.getElementById('user-input');
    const aiOutputP = document.getElementById('ai-output');

    if (!toggleMicBtn) {
        console.error('Required elements not found on the page.');
        return;
    }

    let recognition = null;
    let isListening = false;
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;

    if (SpeechRecognition) {
        recognition = new SpeechRecognition();
        recognition.continuous = false; // Process single utterances
        recognition.lang = 'ko-KR'; // Set to Korean
        recognition.interimResults = false;
        recognition.maxAlternatives = 1;

        recognition.onstart = () => {
            isListening = true;
            statusDiv.textContent = 'Listening...';
            toggleMicBtn.textContent = 'Stop Listening';
            userInputP.textContent = '';
            aiOutputP.textContent = '';
        };

        recognition.onresult = async (event) => {
            const transcript = event.results[0][0].transcript;
            userInputP.textContent = transcript;
            statusDiv.textContent = 'Processing...';

            try {
                const response = await fetch('/api/voice_command', { // Matches FastAPI route
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ text: transcript }),
                });

                const result = await response.json();

                if (response.ok) {
                    aiOutputP.textContent = result.ai_response;
                    // Speak the AI response
                    speak(result.ai_response);
                } else {
                    aiOutputP.textContent = `Error: ${result.error || 'Unknown error'}`;
                    statusDiv.textContent = `Error: ${result.error || 'Unknown error'}`;
                }
            } catch (error) {
                console.error('Error calling voice command API:', error);
                aiOutputP.textContent = 'Error communicating with server.';
                statusDiv.textContent = 'Error communicating with server.';
            }
        };

        recognition.onerror = (event) => {
            console.error('Speech recognition error:', event.error);
            statusDiv.textContent = `Recognition error: ${event.error}`;
            if (event.error === 'no-speech') {
                statusDiv.textContent = 'No speech detected. Please try again.';
            } else if (event.error === 'audio-capture') {
                statusDiv.textContent = 'Microphone error. Please check permissions and hardware.';
            } else if (event.error === 'not-allowed') {
                statusDiv.textContent = 'Microphone access denied. Please allow microphone access in your browser settings.';
            }
            stopListening();
        };

        recognition.onend = () => {
            if (isListening) { // If it ended unexpectedly, try to restart if still intended to listen
                // Or simply stop and let user restart manually
                // recognition.start(); // Example: auto-restart (can lead to loops)
            }
            stopListening(); // Ensure UI updates correctly
        };

    } else {
        statusDiv.textContent = 'Speech recognition not supported by this browser.';
        toggleMicBtn.disabled = true;
    }

    function startListening() {
        if (recognition && !isListening) {
            try {
                recognition.start();
            } catch (e) {
                console.error("Error starting recognition: ", e);
                statusDiv.textContent = "Could not start listener. Another listener might be active.";
            }
        }
    }

    function stopListening() {
        if (recognition && isListening) {
            recognition.stop();
        }
        isListening = false;
        statusDiv.textContent = 'Click "Start Listening" to begin.';
        toggleMicBtn.textContent = 'Start Listening';
    }

    function speak(text) {
        if ('speechSynthesis' in window) {
            const utterance = new SpeechSynthesisUtterance(text);
            utterance.lang = 'ko-KR'; // Speak in Korean
            // You can configure other properties like voice, rate, pitch here
            // e.g. const voices = window.speechSynthesis.getVoices();
            // utterance.voice = voices.find(v => v.lang === 'ko-KR');
            window.speechSynthesis.speak(utterance);
        } else {
            console.warn('Speech synthesis not supported by this browser.');
            // Fallback or message to user
        }
    }

    toggleMicBtn.addEventListener('click', () => {
        if (isListening) {
            stopListening();
        } else {
            startListening();
        }
    });
});
