class ResearchAnalyser {
    constructor() {
        this.baseURL = 'http://localhost:8000';
        this.currentDocId = null;
        this.documents = [];
        this.isUploading = false;
        this.isTyping = false;
        this.isSidebarOpen = window.innerWidth >= 768;

        this.initializeElements();
        this.attachEventListeners();
        this.loadDocuments();
        this.setupAutoResize();
        this.checkBackendConnection();
        this.handleResponsiveDesign();
    }

    initializeElements() {
        // DOM elements
        this.fileInput = document.getElementById('fileInput');
        this.uploadBtn = document.getElementById('uploadBtn');
        this.uploadBtnText = document.getElementById('uploadBtnText');
        this.uploadStatus = document.getElementById('uploadStatus');
        this.uploadProgress = document.getElementById('uploadProgress');
        this.progressBar = document.getElementById('progressBar');
        this.documentsList = document.getElementById('documentsList');
        this.messagesContainer = document.getElementById('messagesContainer');
        this.messageInput = document.getElementById('messageInput');
        this.sendBtn = document.getElementById('sendBtn');
        this.chatTitle = document.getElementById('chatTitle');
        this.currentDocIdElement = document.getElementById('currentDocId');
        this.clearChatBtn = document.getElementById('clearChatBtn');
        this.newChatBtn = document.getElementById('newChatBtn');
        this.loadingModal = document.getElementById('loadingModal');
        this.loadingText = document.getElementById('loadingText');
        this.loadingSubtext = document.getElementById('loadingSubtext');
        this.sidebar = document.getElementById('sidebar');
        this.toggleSidebar = document.getElementById('toggleSidebar');
        this.sidebarBackdrop = document.getElementById('sidebarBackdrop');
        this.refreshDocsBtn = document.getElementById('refreshDocsBtn');
        this.viewAllChatsBtn = document.getElementById('viewAllChatsBtn');
        this.clearAllBtn = document.getElementById('clearAllBtn');
        this.exportChatBtn = document.getElementById('exportChatBtn');
        this.connectionStatus = document.getElementById('connectionStatus');
        this.charCount = document.getElementById('charCount');
        this.typingIndicator = document.getElementById('typingIndicator');
        this.chatHistoryModal = document.getElementById('chatHistoryModal');
        this.closeChatHistoryBtn = document.getElementById('closeChatHistoryBtn');
        this.chatHistoryContent = document.getElementById('chatHistoryContent');
        this.successToast = document.getElementById('successToast');
        this.errorToast = document.getElementById('errorToast');
        this.successMessage = document.getElementById('successMessage');
        this.errorMessage = document.getElementById('errorMessage');
    }

    attachEventListeners() {
        // Upload functionality
        this.uploadBtn.addEventListener('click', () => this.fileInput.click());
        this.fileInput.addEventListener('change', (e) => this.handleFileUpload(e));

        // Send message
        this.sendBtn.addEventListener('click', () => this.sendMessage());
        this.messageInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });

        // Character count
        this.messageInput.addEventListener('input', () => {
            const count = this.messageInput.value.length;
            this.charCount.textContent = count;
            if (count > 1800) {
                this.charCount.classList.add('text-red-500');
            } else {
                this.charCount.classList.remove('text-red-500');
            }
        });

        // Clear chat
        this.clearChatBtn.addEventListener('click', () => this.clearChat());

        // New chat
        this.newChatBtn.addEventListener('click', () => this.startNewChat());

        // Export chat
        this.exportChatBtn.addEventListener('click', () => this.exportChat());

        // Sidebar functionality
        this.toggleSidebar.addEventListener('click', () => this.toggleSidebarVisibility());
        this.sidebarBackdrop.addEventListener('click', () => this.closeSidebar());

        // Refresh documents
        this.refreshDocsBtn.addEventListener('click', () => this.loadDocuments());

        // View all chats
        this.viewAllChatsBtn.addEventListener('click', () => this.showChatHistory());

        // Clear all chats
        this.clearAllBtn.addEventListener('click', () => this.clearAllChats());

        // Chat history modal
        this.closeChatHistoryBtn.addEventListener('click', () => this.closeChatHistoryModal());

        // Window resize
        window.addEventListener('resize', () => this.handleResponsiveDesign());

        // Escape key to close modals
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                this.closeChatHistoryModal();
                if (window.innerWidth < 768) this.closeSidebar();
            }
        });
    }

    setupAutoResize() {
        this.messageInput.addEventListener('input', () => {
            this.messageInput.style.height = 'auto';
            this.messageInput.style.height = Math.min(this.messageInput.scrollHeight, 120) + 'px';
        });
    }

    handleResponsiveDesign() {
        const isMobile = window.innerWidth < 768;
        if (!isMobile) {
            this.sidebar.classList.remove('sidebar-hidden');
            this.sidebarBackdrop.classList.add('hidden');
        } else if (!this.isSidebarOpen) {
            this.sidebar.classList.add('sidebar-hidden');
        }
    }

    toggleSidebarVisibility() {
        this.isSidebarOpen = !this.isSidebarOpen;
        if (window.innerWidth < 768) {
            if (this.isSidebarOpen) {
                this.sidebar.classList.remove('sidebar-hidden');
                this.sidebarBackdrop.classList.remove('hidden');
            } else {
                this.closeSidebar();
            }
        }
    }

    closeSidebar() {
        this.isSidebarOpen = false;
        this.sidebar.classList.add('sidebar-hidden');
        this.sidebarBackdrop.classList.add('hidden');
    }

    async checkBackendConnection() {
        try {
            const response = await fetch(`${this.baseURL}/health`);
            if (response.ok) {
                this.updateConnectionStatus(true);
            } else {
                this.updateConnectionStatus(false);
            }
        } catch (error) {
            console.error('Backend connection failed:', error);
            this.updateConnectionStatus(false);
        }
    }

    updateConnectionStatus(connected) {
        const statusElement = this.connectionStatus.querySelector('div');
        const textElement = this.connectionStatus.querySelector('span');

        if (connected) {
            statusElement.className = 'w-2 h-2 bg-green-500 rounded-full animate-pulse';
            textElement.textContent = 'Connected';
        } else {
            statusElement.className = 'w-2 h-2 bg-red-500 rounded-full';
            textElement.textContent = 'Disconnected';
        }
    }

    showLoading(text = 'Processing...', subtext = '') {
        this.loadingText.textContent = text;
        this.loadingSubtext.textContent = subtext;
        this.loadingModal.classList.remove('hidden');
        this.loadingModal.classList.add('flex');
    }

    hideLoading() {
        this.loadingModal.classList.add('hidden');
        this.loadingModal.classList.remove('flex');
    }

    showToast(message, isError = false) {
        const toast = isError ? this.errorToast : this.successToast;
        const messageElement = isError ? this.errorMessage : this.successMessage;

        messageElement.textContent = message;
        toast.classList.remove('translate-x-full');

        setTimeout(() => {
            toast.classList.add('translate-x-full');
        }, 3000);
    }

    showUploadProgress(visible = true) {
        if (visible) {
            this.uploadProgress.classList.remove('hidden');
            this.uploadBtn.disabled = true;
            this.uploadBtnText.textContent = 'Uploading...';
        } else {
            this.uploadProgress.classList.add('hidden');
            this.uploadBtn.disabled = false;
            this.uploadBtnText.textContent = 'Choose File';
            this.progressBar.style.width = '0%';
        }
    }

    async handleFileUpload(event) {
        const file = event.target.files[0];
        if (!file) return;

        if (this.isUploading) {
            this.showToast('Upload already in progress...', true);
            return;
        }

        this.isUploading = true;
        this.showUploadProgress(true);
        this.showLoading('Uploading and processing document...', 'This may take a few minutes');

        const formData = new FormData();
        formData.append('file', file);

        try {
            // Simulate progress
            let progress = 0;
            const progressInterval = setInterval(() => {
                progress += Math.random() * 20;
                if (progress > 90) progress = 90;
                this.progressBar.style.width = progress + '%';
            }, 200);

            const response = await fetch(`${this.baseURL}/upload/`, {
                method: 'POST',
                body: formData
            });

            clearInterval(progressInterval);
            this.progressBar.style.width = '100%';

            const result = await response.json();

            if (response.ok && result.doc_id) {
                this.showToast(`✓ Document uploaded successfully! ID: ${result.doc_id}`);
                await this.loadDocuments();
                this.selectDocument(result.doc_id, result.filename || file.name);
            } else {
                const errorMsg = result.error || result.detail || 'Upload failed. Please try again.';
                this.showToast(errorMsg, true);
            }
        } catch (error) {
            console.error('Upload error:', error);
            this.showToast('Network error. Please check your connection.', true);
        } finally {
            this.isUploading = false;
            this.showUploadProgress(false);
            this.hideLoading();
            this.fileInput.value = '';
        }
    }

    async loadDocuments() {
        try {
            const response = await fetch(`${this.baseURL}/documents/`);
            if (!response.ok) throw new Error('Failed to fetch documents');

            const documents = await response.json();
            this.documents = Array.isArray(documents) ? documents : [];
            this.renderDocuments();
        } catch (error) {
            console.error('Error loading documents:', error);
            this.showToast('Failed to load documents', true);
        }
    }

    renderDocuments() {
        const container = this.documentsList;

        if (this.documents.length === 0) {
            container.innerHTML = `
                <div class="text-center text-warm-grey py-8">
                    <i class="fas fa-file-alt text-3xl mb-2 opacity-60"></i>
                    <p class="text-sm">No documents uploaded yet</p>
                </div>
            `;
            return;
        }

        container.innerHTML = this.documents.map(doc => `
            <div class="document-item p-3 bg-white hover:bg-golden-yellow hover:bg-opacity-20 rounded-lg cursor-pointer transition-all duration-200 border border-transparent hover:border-primary-orange ${this.currentDocId === doc.doc_id ? 'document-selected' : ''}"
                 onclick="researchAnalyser.selectDocument('${doc.doc_id}', '${doc.filename}')"
                <div class="flex items-center justify-between">
                    <div class="flex-1 min-w-0">
                        <p class="text-sm font-medium truncate text-deep-brown">${doc.filename}</p>
                        <p class="text-xs text-warm-brown">${new Date(doc.upload_date).toLocaleDateString()}</p>
                        <p class="text-xs text-accent font-mono bg-warm-grey bg-opacity-20 px-2 py-1 rounded mt-1 inline-block">
                            ${doc.doc_id.slice(0, 8)}...
                        </p>
                    </div>
                    <div class="flex flex-col items-center gap-2 ml-2">
                        <i class="fas fa-file-alt text-accent"></i>
                        <button class="text-xs text-warm-brown hover:text-deep-brown transition-colors" 
                                onclick="event.stopPropagation(); researchAnalyser.viewDocumentHistory('${doc.doc_id}')">
                            <i class="fas fa-history"></i>
                        </button>
                    </div>
                </div>
            </div>
        `).join('');
    }

    async selectDocument(docId, filename) {
        this.currentDocId = docId;
        this.chatTitle.textContent = filename;
        this.currentDocIdElement.textContent = `Doc ID: ${docId}`;

        // Enable controls
        this.messageInput.disabled = false;
        this.sendBtn.disabled = false;
        this.clearChatBtn.disabled = false;
        this.exportChatBtn.disabled = false;
        this.messageInput.placeholder = `Ask questions about ${filename}...`;

        // Update document selection in UI
        this.renderDocuments();

        // Load chat history for this document
        await this.loadChatHistory(docId);

        // Close sidebar on mobile after selection
        if (window.innerWidth < 768) {
            this.closeSidebar();
        }
    }

    async loadChatHistory(docId) {
        try {
            const response = await fetch(`${this.baseURL}/chat-history?doc_id=${docId}`);
            const result = await response.json();

            this.messagesContainer.innerHTML = '';

            if (result.chat_history && result.chat_history.length > 0) {
                result.chat_history.forEach(entry => {
                    this.addMessage(entry.query, 'user', false, new Date(entry.created_at));
                    this.addMessage(entry.answer, 'assistant', false, new Date(entry.created_at));
                });
            } else {
                this.showWelcomeMessage();
            }

            this.scrollToBottom();
        } catch (error) {
            console.error('Error loading chat history:', error);
            this.showWelcomeMessage();
        }
    }

    showWelcomeMessage() {
        this.messagesContainer.innerHTML = `
            <div class="text-center text-warm-brown mt-20">
                <div class="bg-gradient-to-br from-accent to-amber w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
                    <i class="fas fa-comments text-2xl text-deep-brown"></i>
                </div>
                <h3 class="text-xl mb-2 font-semibold text-deep-brown">Start chatting with ${this.chatTitle.textContent}</h3>
                <p class="text-sm text-soft-brown max-w-md mx-auto">Ask any question about the document content. I'll provide detailed answers with citations.</p>
            </div>
        `;
    }

    async sendMessage() {
        const message = this.messageInput.value.trim();
        if (!message || !this.currentDocId || this.isTyping) return;

        // Add user message to chat
        this.addMessage(message, 'user');
        this.messageInput.value = '';
        this.messageInput.style.height = 'auto';
        this.charCount.textContent = '0';

        // Show typing indicator
        this.showTypingIndicator(true);

        try {
            const response = await fetch(`${this.baseURL}/chat/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    doc_id: this.currentDocId,
                    question: message
                })
            });

            const result = await response.json();

            // Hide typing indicator
            this.showTypingIndicator(false);

            if (result.error) {
                this.addMessage(`Error: ${result.error}`, 'assistant', true);
            } else {
                this.addMessage(result.answer, 'assistant');
                if (result.citations && result.citations.length > 0) {
                    this.addCitations(result.citations);
                }
            }

        } catch (error) {
            this.showTypingIndicator(false);
            this.addMessage('Sorry, there was an error processing your request. Please try again.', 'assistant', true);
            console.error('Chat error:', error);
        }
    }

    addMessage(content, sender, isError = false, timestamp = new Date()) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `flex ${sender === 'user' ? 'justify-end' : 'justify-start'} message-bubble`;

        const bubble = document.createElement('div');
        bubble.className = `max-w-4xl p-4 rounded-xl shadow-lg ${
            sender === 'user' 
                ? 'bg-primary-orange text-white ml-12' 
                : isError 
                    ? 'bg-red-400 text-white mr-12'
                    : 'bg-white text-deep-brown mr-12 border border-border-brown'
        }`;

        // Format content with markdown-style formatting
        const formattedContent = this.formatMessage(content);

        bubble.innerHTML = `
            <div class="flex items-start gap-3">
                <div class="flex-shrink-0 mt-1">
                    <div class="w-8 h-8 rounded-full ${sender === 'user' ? 'bg-white bg-opacity-30' : 'bg-primary-orange'} flex items-center justify-center">
                        <i class="fas ${sender === 'user' ? 'fa-user' : 'fa-robot'} text-sm ${sender === 'user' ? 'text-white' : 'text-white'}"></i>
                    </div>
                </div>
                <div class="flex-1 min-w-0">
                    <div class="flex items-center gap-2 mb-1">
                        <span class="text-sm font-medium">${sender === 'user' ? 'You' : 'AI Assistant'}</span>
                        <span class="text-xs opacity-70">${timestamp.toLocaleTimeString()}</span>
                    </div>
                    <div class="prose prose-invert max-w-none text-sm leading-relaxed">${formattedContent}</div>
                </div>
            </div>
        `;

        messageDiv.appendChild(bubble);
        this.messagesContainer.appendChild(messageDiv);
        this.scrollToBottom();
    }

    formatMessage(content) {
        return content
            .replace(/\n/g, '<br>')
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/\*(.*?)\*/g, '<em>$1</em>')
            .replace(/`(.*?)`/g, '<code class="bg-warm-grey bg-opacity-20 px-1 py-0.5 rounded text-accent">$1</code>');
    }

    addCitations(citations) {
        if (citations.length === 0) return;

        const citationsDiv = document.createElement('div');
        citationsDiv.className = 'flex justify-start message-bubble';

        const bubble = document.createElement('div');
        bubble.className = 'max-w-4xl p-3 bg-golden-yellow bg-opacity-15 text-deep-brown rounded-xl mr-12 ml-14 border border-border-brown';

        bubble.innerHTML = `
            <div class="text-sm font-medium mb-3 flex items-center gap-2">
                <i class="fas fa-quote-left text-primary-orange"></i>
                <span>Source Citations</span>
            </div>
            ${citations.map((citation, index) => `
                <div class="text-xs border-l-2 border-primary-orange pl-3 py-1 mb-2 bg-white bg-opacity-50 rounded-r">
                    <div class="flex items-center gap-2 mb-1">
                        <span class="bg-primary-orange text-white px-2 py-0.5 rounded text-xs font-medium">${index + 1}</span>
                        <span class="text-primary-orange text-xs">${citation.confidence || 'medium'} confidence</span>
                    </div>
                    <p class="text-warm-brown">${citation.excerpt}</p>
                </div>
            `).join('')}
        `;

        citationsDiv.appendChild(bubble);
        this.messagesContainer.appendChild(citationsDiv);
        this.scrollToBottom();
    }

    showTypingIndicator(show = true) {
        this.isTyping = show;
        const indicator = document.getElementById('typingIndicator');
        if (show) {
            indicator.classList.remove('hidden');
        } else {
            indicator.classList.add('hidden');
        }
    }

    async clearChat() {
        if (!this.currentDocId) return;

        if (confirm('Are you sure you want to clear this chat? This action cannot be undone.')) {
            this.showWelcomeMessage();
            this.showToast('Chat cleared successfully');
        }
    }

    startNewChat() {
        this.currentDocId = null;
        this.chatTitle.textContent = 'Select a document to start chatting';
        this.currentDocIdElement.textContent = '';
        this.messageInput.disabled = true;
        this.sendBtn.disabled = true;
        this.clearChatBtn.disabled = true;
        this.exportChatBtn.disabled = true;
        this.messageInput.placeholder = 'Select a document first...';

        this.messagesContainer.innerHTML = `
            <div class="text-center text-warm-brown mt-20">
                <div class="bg-gradient-to-br from-accent to-amber w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
                    <i class="fas fa-brain text-2xl text-deep-brown"></i>
                </div>
                <h3 class="text-xl mb-2 font-semibold text-deep-brown">Welcome to Research Analyser</h3>
                <p class="text-sm text-soft-brown max-w-md mx-auto">Upload a document to begin your intelligent research conversation.</p>
            </div>
        `;

        this.renderDocuments();
    }

    async exportChat() {
        if (!this.currentDocId) return;

        try {
            const response = await fetch(`${this.baseURL}/chat-history?doc_id=${this.currentDocId}`);
            const result = await response.json();

            if (result.chat_history) {
                const chatData = {
                    document: this.chatTitle.textContent,
                    doc_id: this.currentDocId,
                    exported_at: new Date().toISOString(),
                    chat_history: result.chat_history
                };

                const blob = new Blob([JSON.stringify(chatData, null, 2)], { type: 'application/json' });
                const url = URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `chat_${this.currentDocId}_${Date.now()}.json`;
                document.body.appendChild(a);
                a.click();
                document.body.removeChild(a);
                URL.revokeObjectURL(url);

                this.showToast('Chat exported successfully');
            }
        } catch (error) {
            console.error('Export error:', error);
            this.showToast('Failed to export chat', true);
        }
    }

    async showChatHistory() {
        this.showLoading('Loading chat history...', 'Please wait');

        try {
            const allChats = {};

            for (const doc of this.documents) {
                const response = await fetch(`${this.baseURL}/chat-history?doc_id=${doc.doc_id}`);
                const result = await response.json();

                if (result.chat_history && result.chat_history.length > 0) {
                    allChats[doc.doc_id] = {
                        filename: doc.filename,
                        upload_date: doc.upload_date,
                        chats: result.chat_history
                    };
                }
            }

            this.renderChatHistory(allChats);
            this.chatHistoryModal.classList.remove('hidden');
            this.chatHistoryModal.classList.add('flex');
        } catch (error) {
            console.error('Error loading chat history:', error);
            this.showToast('Failed to load chat history', true);
        } finally {
            this.hideLoading();
        }
    }

    renderChatHistory(allChats) {
        const container = this.chatHistoryContent;

        if (Object.keys(allChats).length === 0) {
            container.innerHTML = `
                <div class="text-center text-warm-brown py-8">
                    <i class="fas fa-history text-4xl mb-4 opacity-60"></i>
                    <h3 class="text-lg mb-2 text-deep-brown">No Chat History</h3>
                    <p class="text-sm">Start chatting with your documents to see history here.</p>
                </div>
            `;
            return;
        }

        container.innerHTML = Object.entries(allChats).map(([docId, data]) => `
            <div class="bg-white bg-opacity-60 rounded-lg p-4 mb-4">
                <div class="flex items-center justify-between mb-3">
                    <div>
                        <h4 class="font-medium text-lg text-deep-brown">${data.filename}</h4>
                        <p class="text-sm text-warm-brown">Uploaded: ${new Date(data.upload_date).toLocaleDateString()}</p>
                        <p class="text-xs text-accent font-mono">${docId}</p>
                    </div>
                    <button onclick="researchAnalyser.viewDocumentHistory('${docId}')" 
                            class="bg-accent hover:bg-accent-hover px-4 py-2 rounded-lg transition-colors text-deep-brown">
                        <i class="fas fa-eye mr-1"></i> View Chat
                    </button>
                </div>
                <div class="text-sm text-warm-brown">
                    <strong>${data.chats.length}</strong> messages in this conversation
                </div>
            </div>
        `).join('');
    }

    async viewDocumentHistory(docId) {
        const doc = this.documents.find(d => d.doc_id === docId);
        if (doc) {
            await this.selectDocument(docId, doc.filename);
            this.closeChatHistoryModal();
        }
    }

    closeChatHistoryModal() {
        this.chatHistoryModal.classList.add('hidden');
        this.chatHistoryModal.classList.remove('flex');
    }

    async clearAllChats() {
        if (confirm('Are you sure you want to clear ALL chat history? This action cannot be undone.')) {
            this.showToast('All chats cleared (Note: This is a local action only)');
            this.startNewChat();
        }
    }

    scrollToBottom() {
        setTimeout(() => {
            this.messagesContainer.scrollTop = this.messagesContainer.scrollHeight;
        }, 100);
    }
}

// Initialize the application
const researchAnalyser = new ResearchAnalyser();

// Handle service worker for offline functionality (optional)
if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
        navigator.serviceWorker.register('/sw.js').catch(() => {
            // Service worker registration failed - not critical
        });
    });
}