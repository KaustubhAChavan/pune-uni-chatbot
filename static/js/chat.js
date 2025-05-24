document.addEventListener('DOMContentLoaded', function() {
    // DOM Elements
    const chatMessages = document.getElementById('chat-messages');
    const messageInput = document.getElementById('message-input');
    const sendButton = document.getElementById('send-button');
    const voiceInputButton = document.getElementById('voice-input-button');
    const quickActionButtons = document.querySelectorAll('.quick-action-button');
    const tabButtons = document.querySelectorAll('.tab-button');
    const tabContents = document.querySelectorAll('.tab-content');
    const audioPlayer = document.getElementById('audio-player');
    
    // Initialize quick action buttons
    document.querySelectorAll('.quick-action-button').forEach(button => {
        button.addEventListener('click', function() {
            const category = this.getAttribute('data-category');
            handleQuickAction(category);
        });
    });
    
    // Show the active tab content
    function showTab(tabId) {
        // Hide all tab contents
        tabContents.forEach(content => {
            content.classList.remove('active');
        });
        
        // Remove active class from all tab buttons
        tabButtons.forEach(button => {
            button.classList.remove('active');
        });
        
        // Show the selected tab content
        document.getElementById(`${tabId}-tab`).classList.add('active');
        
        // Add active class to the clicked tab button
        document.querySelector(`[data-tab="${tabId}"]`).classList.add('active');
        
        // Load specific tab content if needed
        if (tabId === 'resources') {
            loadResources();
        } else if (tabId === 'notifications') {
            loadNotifications();
        } else if (tabId === 'quick-access') {
            // Nothing to load initially for quick access
        }
    }
    
    // Add event listeners to tab buttons
    tabButtons.forEach(button => {
        button.addEventListener('click', () => {
            const tabId = button.getAttribute('data-tab');
            showTab(tabId);
        });
    });
    
    // Handle message input changes
    messageInput.addEventListener('input', function() {
        // Enable or disable send button based on input
        if (this.value.trim() !== '') {
            sendButton.classList.add('active');
        } else {
            sendButton.classList.remove('active');
        }
    });
    
    // Add event listener for Enter key
    messageInput.addEventListener('keypress', function(event) {
        if (event.key === 'Enter' && this.value.trim() !== '') {
            sendMessage();
        }
    });
    
    // Send button click handler
    sendButton.addEventListener('click', function() {
        if (messageInput.value.trim() !== '') {
            sendMessage();
        }
    });
    
    // Voice input button click handler
    voiceInputButton.addEventListener('click', function() {
        startVoiceInput();
    });
    
    // Quick action handler
    function handleQuickAction(category) {
        // Show loading message
        addMessage(`Getting information about ${category}...`, 'user');
        
        const loadingMessage = addLoadingMessage();
        
        // Send request to server
        fetch(`/api/quick-access/${category}`)
            .then(response => response.json())
            .then(data => {
                // Remove loading message
                loadingMessage.remove();
                
                // Add response
                addMessage(data.response, 'bot', data.sources);
                
                // Scroll to bottom
                scrollToBottom();
            })
            .catch(error => {
                console.error('Error:', error);
                loadingMessage.remove();
                addMessage(`Sorry, I couldn't get information about ${category}. Please try again later.`, 'bot');
            });
    }
    
    // Send chat message
    function sendMessage() {
        const message = messageInput.value.trim();
        if (message === '') return;
        
        // Add user message to chat
        addMessage(message, 'user');
        
        // Clear input
        messageInput.value = '';
        sendButton.classList.remove('active');
        
        // Show loading indicator
        const loadingMessage = addLoadingMessage();
        
        // Send request to server
        fetch('/api/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ message: message }),
        })
        .then(response => response.json())
        .then(data => {
            // Remove loading message
            loadingMessage.remove();
            
            // Add bot response
            addMessage(data.response, 'bot', data.sources);
            
            // Scroll to bottom
            scrollToBottom();
        })
        .catch(error => {
            console.error('Error:', error);
            loadingMessage.remove();
            addMessage('Sorry, there was an error processing your request.', 'bot');
        });
    }
    
    // Add a message to the chat
    function addMessage(text, sender, sources = []) {
        const messageDiv = document.createElement('div');
        messageDiv.classList.add('message', sender);
        
        const messageBubble = document.createElement('div');
        messageBubble.classList.add('message-bubble');
        
        // Parse markdown-like formatting
        let formattedText = text
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/\*(.*?)\*/g, '<em>$1</em>')
            .replace(/\n/g, '<br>');
        
        // Create paragraphs
        const paragraphs = formattedText.split('<br><br>');
        paragraphs.forEach(paragraph => {
            if (paragraph.trim()) {
                const p = document.createElement('p');
                p.innerHTML = paragraph.replace(/<br>/g, '<br>');
                messageBubble.appendChild(p);
            }
        });
        
        messageDiv.appendChild(messageBubble);
        
        // Add sources if available
        if (sender === 'bot' && sources && sources.length > 0) {
            const sourcesText = document.createElement('p');
            sourcesText.classList.add('sources');
            sourcesText.innerHTML = `<small><em>Sources: ${sources.join(', ')}</em></small>`;
            messageBubble.appendChild(sourcesText);
        }
        
        // Add speak button for bot messages
        if (sender === 'bot') {
            const messageActions = document.createElement('div');
            messageActions.classList.add('message-actions');
            
            const speakButton = document.createElement('button');
            speakButton.classList.add('speak-button');
            speakButton.setAttribute('data-text', text);
            speakButton.innerHTML = '<i class="fas fa-volume-up"></i>';
            
            speakButton.addEventListener('click', function() {
                speakText(text);
            });
            
            messageActions.appendChild(speakButton);
            messageDiv.appendChild(messageActions);
        }
        
        chatMessages.appendChild(messageDiv);
        scrollToBottom();
        
        return messageDiv;
    }
    
    // Add loading message
    function addLoadingMessage() {
        const loadingDiv = document.createElement('div');
        loadingDiv.classList.add('message', 'bot');
        
        const loadingBubble = document.createElement('div');
        loadingBubble.classList.add('message-bubble', 'loading-bubble');
        
        const loadingDots = document.createElement('div');
        loadingDots.classList.add('loading-dots');
        loadingDots.innerHTML = '<span>.</span><span>.</span><span>.</span>';
        
        loadingBubble.appendChild(loadingDots);
        loadingDiv.appendChild(loadingBubble);
        
        chatMessages.appendChild(loadingDiv);
        scrollToBottom();
        
        return loadingDiv;
    }
    
    // Scroll chat to bottom
    function scrollToBottom() {
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
    
    // Convert text to speech
    function speakText(text) {
        // First stop any currently playing audio
        audioPlayer.pause();
        
        // Show loading state on speak button
        const speakButtons = document.querySelectorAll('.speak-button');
        let clickedButton = null;
        
        speakButtons.forEach(button => {
            if (button.getAttribute('data-text') === text) {
                clickedButton = button;
                const icon = button.querySelector('i');
                icon.classList.remove('fa-volume-up');
                icon.classList.add('fa-spinner', 'fa-spin');
            }
        });
        
        // Request speech synthesis from server
        fetch('/api/speak', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ text: text }),
        })
        .then(response => response.json())
        .then(data => {
            if (data.audio_url) {
                audioPlayer.src = data.audio_url;
                audioPlayer.play();
                
                // Reset button state when audio starts playing
                if (clickedButton) {
                    const icon = clickedButton.querySelector('i');
                    icon.classList.remove('fa-spinner', 'fa-spin');
                    icon.classList.add('fa-volume-up');
                }
            }
        })
        .catch(error => {
            console.error('Error:', error);
            
            // Reset button state on error
            if (clickedButton) {
                const icon = clickedButton.querySelector('i');
                icon.classList.remove('fa-spinner', 'fa-spin');
                icon.classList.add('fa-volume-up');
            }
        });
    }
    
    // Start voice input
    function startVoiceInput() {
        // Check if browser supports speech recognition
        if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
            alert('Your browser does not support speech recognition. Please try a different browser.');
            return;
        }
        
        // Create speech recognition object
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        const recognition = new SpeechRecognition();
        
        // Configure recognition
        recognition.lang = 'en-IN';
        recognition.interimResults = false;
        recognition.maxAlternatives = 1;
        
        // Change button to indicate recording
        voiceInputButton.innerHTML = '<i class="fas fa-microphone-slash"></i>';
        voiceInputButton.classList.add('recording');
        
        // Start recognition
        recognition.start();
        
        // Event listeners
        recognition.onresult = function(event) {
            const transcript = event.results[0][0].transcript;
            messageInput.value = transcript;
            
            // Enable send button
            sendButton.classList.add('active');
        };
        
        recognition.onend = function() {
            // Reset button
            voiceInputButton.innerHTML = '<i class="fas fa-microphone"></i>';
            voiceInputButton.classList.remove('recording');
            
            // Send message if we got something
            if (messageInput.value.trim() !== '') {
                sendMessage();
            }
        };
        
        recognition.onerror = function(event) {
            console.error('Speech recognition error', event.error);
            
            // Reset button
            voiceInputButton.innerHTML = '<i class="fas fa-microphone"></i>';
            voiceInputButton.classList.remove('recording');
            
            // Show error message
            if (event.error === 'not-allowed') {
                addMessage('Microphone access was denied. Please allow microphone access to use voice input.', 'bot');
            } else {
                addMessage('There was an error with voice recognition. Please try again.', 'bot');
            }
        };
    }
    
    // Load resources from API
    function loadResources() {
        const resourcesList = document.getElementById('resources-list');
        
        // Show loading state
        resourcesList.innerHTML = '<div class="loading">Loading resources...</div>';
        
        // Fetch resources from server
        fetch('/api/resources')
            .then(response => response.json())
            .then(data => {
                // Clear loading state
                resourcesList.innerHTML = '';
                
                // Add resources to list
                if (data && data.length > 0) {
                    data.forEach(resource => {
                        const resourceCard = document.createElement('div');
                        resourceCard.classList.add('resource-card');
                        
                        resourceCard.innerHTML = `
                            <h3>${resource.title}</h3>
                            <a href="${resource.url}" class="resource-link" target="_blank">
                                Visit resource <i class="fas fa-external-link-alt"></i>
                            </a>
                        `;
                        
                        resourcesList.appendChild(resourceCard);
                    });
                } else {
                    resourcesList.innerHTML = '<div class="empty-state">No resources available</div>';
                }
            })
            .catch(error => {
                console.error('Error:', error);
                resourcesList.innerHTML = '<div class="error-state">Failed to load resources. Please try again later.</div>';
            });
    }
    
    // Load notifications from API
    function loadNotifications() {
        const notificationsList = document.getElementById('notifications-list');
        
        // Show loading state
        notificationsList.innerHTML = '<div class="loading">Loading notifications...</div>';
        
        // Fetch notifications from server
        fetch('/api/notifications')
            .then(response => response.json())
            .then(data => {
                // Clear loading state
                notificationsList.innerHTML = '';
                
                // Add notifications to list
                if (data && data.length > 0) {
                    data.forEach(notification => {
                        const notificationCard = document.createElement('div');
                        notificationCard.classList.add('notification-card');
                        
                        if (!notification.read) {
                            notificationCard.classList.add('unread');
                        }
                        
                        // Determine icon based on notification type or content
                        let iconClass = 'fa-bell';
                        if (notification.title.toLowerCase().includes('exam')) {
                            iconClass = 'fa-calendar-alt';
                        } else if (notification.title.toLowerCase().includes('scholarship')) {
                            iconClass = 'fa-award';
                        } else if (notification.title.toLowerCase().includes('holiday')) {
                            iconClass = 'fa-calendar-day';
                        }
                        
                        notificationCard.innerHTML = `
                            <div class="notification-icon">
                                <i class="fas ${iconClass}"></i>
                            </div>
                            <div class="notification-content">
                                <div class="notification-title">${notification.title}</div>
                                <div class="notification-text">${notification.content}</div>
                                <div class="notification-date">${notification.date}</div>
                            </div>
                            ${!notification.read ? '<div class="notification-unread-dot"></div>' : ''}
                        `;
                        
                        notificationsList.appendChild(notificationCard);
                    });
                } 
            })
            .catch(error => {
                console.error('Error:', error);
                notificationsList.innerHTML = '<div class="error-state">Failed to load notifications. Please try again later.</div>';
            });
    }
    
    // Initialize quick access tab functionality
    document.querySelectorAll('.quick-access-card').forEach(card => {
        card.addEventListener('click', function() {
            const category = this.getAttribute('data-category');
            const resultContainer = document.getElementById('quick-access-content');
            const resultTitle = document.querySelector('.quick-access-result h3');
            
            // Set title
            resultTitle.textContent = category;
            
            // Show loading state
            resultContainer.innerHTML = '<div class="loading">Loading information...</div>';
            
            // Fetch data from server
            fetch(`/api/quick-access/${category}`)
                .then(response => response.json())
                .then(data => {
                    // Format and display the result
                    let formattedContent = data.response
                        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
                        .replace(/\*(.*?)\*/g, '<em>$1</em>')
                        .replace(/\n/g, '<br>');
                    
                    resultContainer.innerHTML = `
                        <div class="quick-access-content-text">
                            ${formattedContent}
                        </div>
                        ${data.sources && data.sources.length > 0 ? 
                            `<div class="quick-access-sources">
                                <small><em>Sources: ${data.sources.join(', ')}</em></small>
                            </div>` : ''}
                    `;
                })
                .catch(error => {
                    console.error('Error:', error);
                    resultContainer.innerHTML = '<div class="error-state">Failed to load information. Please try again later.</div>';
                });
        });
    });
    
    // Initialize the chat interface
    // Add a slight delay for the welcome message to seem more natural
    setTimeout(() => {
        // Nothing needed here since we already have a welcome message in the HTML
    }, 500);
});