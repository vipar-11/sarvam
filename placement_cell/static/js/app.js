// --- DOM Elements ---
const companiesList = document.getElementById('companies-list');
const btnAddCompany = document.getElementById('btn-add-company');
const btnResetSession = document.getElementById('btn-reset-session');
const sessionStateBadge = document.getElementById('session-state');
const assistantStatusText = document.getElementById('assistant-status');
const micContainer = document.querySelector('.mic-container');
const btnTalk = document.getElementById('btn-talk');
const toggleVad = document.getElementById('toggle-vad');
const btnVoiceToggle = document.getElementById('btn-voice-toggle');
const chatLogs = document.getElementById('chat-logs');
const visualizerCanvas = document.getElementById('waveform-visualizer');

// Text Chat inputs
const chatTextInput = document.getElementById('chat-text-input');
const btnSendText = document.getElementById('btn-send-text');

// CV Display & Forms
const cvName = document.getElementById('cv-name');
const cvEmail = document.getElementById('cv-email');
const cvBranch = document.getElementById('cv-branch');
const cvCgpa = document.getElementById('cv-cgpa');
const cvSkills = document.getElementById('cv-skills');
const btnEditCv = document.getElementById('btn-edit-cv');
const cvDisplay = document.getElementById('cv-display');
const cvForm = document.getElementById('cv-form');
const btnCancelCv = document.getElementById('btn-cancel-cv');

// CV Form inputs
const inputCvName = document.getElementById('input-cv-name');
const inputCvEmail = document.getElementById('input-cv-email');
const inputCvBranch = document.getElementById('input-cv-branch');
const inputCvCgpa = document.getElementById('input-cv-cgpa');
const inputCvSkills = document.getElementById('input-cv-skills');

// Modal Elements
const companyModal = document.getElementById('company-modal');
const btnCloseModal = document.getElementById('btn-close-modal');
const btnCancelModal = document.getElementById('btn-cancel-modal');
const companyForm = document.getElementById('company-form');
const modalTitle = document.getElementById('modal-title');
const companyIdInput = document.getElementById('company-id-input');
const companyNameInput = document.getElementById('company-name');
const companyScheduleInput = document.getElementById('company-schedule');
const companySlotInput = document.getElementById('company-slot');
const companyCutoffInput = document.getElementById('company-cutoff');
const companyBranchesInput = document.getElementById('company-branches');
const companyEligibilityInput = document.getElementById('company-eligibility');

// --- Global App State Variables ---
let wsConnection = null;
let isVoiceActive = false;
let isRecording = false;
let isAgentSpeaking = false;
let isAgentSending = false; // Tracks if backend is actively streaming speech chunks
let activeMode = 'voice';   // 'voice' or 'text'
let pendingTextMessage = null;
let audioContext = null;
let micStream = null;
let processorNode = null;

// Audio Playback & Scheduling Variables
let audioCtx = null;
let playbackAnalyser = null;
let micAnalyser = null;
let activeAnalyser = null;
let visualizeActive = false;
let nextPlayTime = 0;              // Schedules continuous speech play back-to-back
let playingSourceNodes = [];       // List of scheduled nodes currently playing/queued

// Canvas setup
const ctx = visualizerCanvas.getContext('2d');
visualizerCanvas.width = 200;
visualizerCanvas.height = 200;

// VAD thresholds
let silenceStart = null;
const SILENCE_THRESHOLD = 0.010;
const SILENCE_DURATION = 1500;

// --- Initialize App ---
document.addEventListener('DOMContentLoaded', () => {
    loadCompanies();
    loadCV();
    setupCanvas();
    drawAmbientWave();
    
    btnVoiceToggle.addEventListener('click', toggleVoiceAssistant);
    btnTalk.addEventListener('click', handleMicButtonClick);
    btnResetSession.addEventListener('click', resetSession);
    
    // Text input handlers
    btnSendText.addEventListener('click', sendTextMessage);
    chatTextInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') {
            sendTextMessage();
        }
    });
    chatTextInput.addEventListener('focus', () => {
        if (isRecording) {
            abortMicStream();
        }
    });
    
    // CV Handlers
    btnEditCv.addEventListener('click', toggleCvEditMode);
    btnCancelCv.addEventListener('click', toggleCvEditMode);
    cvForm.addEventListener('submit', handleCvSubmit);
    
    // Modal Handlers
    btnAddCompany.addEventListener('click', () => showCompanyModal());
    btnCloseModal.addEventListener('click', hideCompanyModal);
    btnCancelModal.addEventListener('click', hideCompanyModal);
    companyForm.addEventListener('submit', handleCompanySubmit);
});

// Setup canvas bounds
function setupCanvas() {
    const rect = visualizerCanvas.getBoundingClientRect();
    visualizerCanvas.width = rect.width;
    visualizerCanvas.height = rect.height;
}

// --- Rest API Operations ---

async function loadCompanies() {
    try {
        const response = await fetch('/api/companies');
        const companies = await response.json();
        renderCompanies(companies);
    } catch (e) {
        console.error('Error loading companies:', e);
        companiesList.innerHTML = '<div class="system-message error">Failed to load company schedule.</div>';
    }
}

function renderCompanies(companies) {
    if (companies.length === 0) {
        companiesList.innerHTML = '<div class="system-message">No companies scheduled yet.</div>';
        return;
    }
    
    companiesList.innerHTML = '';
    companies.forEach(company => {
        const card = document.createElement('div');
        card.className = 'company-card';
        const initial = company.name ? company.name.charAt(0) : 'C';
        card.innerHTML = `
            <div class="company-card-header">
                <div class="company-logo-badge">${initial}</div>
                <div class="company-title-wrap">
                    <h3>${company.name}</h3>
                    <div class="company-date"><i class="fa-regular fa-calendar"></i> ${company.schedule}</div>
                </div>
            </div>
            <div class="company-details">
                <div class="company-detail-item">
                    <i class="fa-regular fa-clock"></i>
                    <span>Slot: ${company.slot}</span>
                </div>
                <div class="company-detail-item">
                    <i class="fa-solid fa-graduation-cap"></i>
                    <span>Eligibility: ${company.eligibility}</span>
                </div>
            </div>
            <div class="company-card-actions">
                <button class="btn btn-secondary btn-sm btn-edit-c" data-id="${company.id}"><i class="fa-regular fa-pen-to-square"></i> Edit</button>
                <button class="btn btn-danger btn-sm btn-delete-c" data-id="${company.id}"><i class="fa-regular fa-trash-can"></i> Delete</button>
            </div>
        `;
        companiesList.appendChild(card);
    });
    
    document.querySelectorAll('.btn-edit-c').forEach(btn => {
        btn.addEventListener('click', (e) => {
            const id = e.currentTarget.getAttribute('data-id');
            editCompany(id, companies);
        });
    });
    
    document.querySelectorAll('.btn-delete-c').forEach(btn => {
        btn.addEventListener('click', async (e) => {
            const id = e.currentTarget.getAttribute('data-id');
            if (confirm('Are you sure you want to delete this company?')) {
                await deleteCompany(id);
            }
        });
    });
}

async function deleteCompany(id) {
    try {
        const response = await fetch(`/api/companies/${id}`, { method: 'DELETE' });
        if (response.ok) {
            loadCompanies();
        } else {
            alert('Failed to delete company.');
        }
    } catch (e) {
        console.error('Delete error:', e);
    }
}

function editCompany(id, companies) {
    const company = companies.find(c => c.id === id);
    if (company) {
        showCompanyModal(company);
    }
}

function showCompanyModal(company = null) {
    companyModal.classList.remove('hidden');
    if (company) {
        modalTitle.innerText = 'Edit IT Company';
        companyIdInput.value = company.id;
        companyNameInput.value = company.name;
        companyScheduleInput.value = company.schedule;
        companySlotInput.value = company.slot;
        companyCutoffInput.value = company.cgpa_cutoff;
        companyBranchesInput.value = company.allowed_branches.join(', ');
        companyEligibilityInput.value = company.eligibility;
        companyIdInput.disabled = true;
    } else {
        modalTitle.innerText = 'Add IT Company';
        companyIdInput.value = '';
        companyNameInput.value = '';
        companyScheduleInput.value = '';
        companySlotInput.value = '';
        companyCutoffInput.value = '';
        companyBranchesInput.value = 'CSE, IT';
        companyEligibilityInput.value = '';
        companyIdInput.disabled = false;
    }
}

function hideCompanyModal() {
    companyModal.classList.add('hidden');
    companyForm.reset();
}

async function handleCompanySubmit(e) {
    e.preventDefault();
    const id = companyIdInput.value.trim().toLowerCase() || companyNameInput.value.trim().toLowerCase().replace(/\s+/g, '-');
    const branches = companyBranchesInput.value.split(',').map(b => b.trim().toUpperCase());
    
    const companyData = {
        id: id,
        name: companyNameInput.value.trim(),
        schedule: companyScheduleInput.value,
        slot: companySlotInput.value.trim(),
        cgpa_cutoff: parseFloat(companyCutoffInput.value),
        allowed_branches: branches,
        eligibility: companyEligibilityInput.value.trim()
    };
    
    const isEdit = companyIdInput.disabled;
    
    try {
        let response;
        if (isEdit) {
            response = await fetch(`/api/companies/${id}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(companyData)
            });
        } else {
            response = await fetch('/api/companies', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(companyData)
            });
        }
        
        if (response.ok) {
            hideCompanyModal();
            loadCompanies();
        } else {
            const err = await response.json();
            alert(`Error: ${err.detail || 'Failed to save company.'}`);
        }
    } catch (e) {
        console.error('Error saving company:', e);
    }
}

// Student CV Operations
async function loadCV() {
    try {
        const response = await fetch('/api/cv');
        const cv = await response.json();
        renderCV(cv);
    } catch (e) {
        console.error('Error loading CV:', e);
    }
}

function renderCV(cv) {
    cvName.innerText = cv.name || '-';
    cvEmail.innerText = cv.email || '-';
    cvBranch.innerText = cv.branch || '-';
    cvCgpa.innerText = cv.cgpa !== undefined ? cv.cgpa.toFixed(2) : '-';
    cvSkills.innerText = cv.skills || '-';
    
    inputCvName.value = cv.name || '';
    inputCvEmail.value = cv.email || '';
    inputCvBranch.value = cv.branch || '';
    inputCvCgpa.value = cv.cgpa || '';
    inputCvSkills.value = cv.skills || '';
}

function toggleCvEditMode() {
    cvDisplay.classList.toggle('hidden');
    cvForm.classList.toggle('hidden');
}

async function handleCvSubmit(e) {
    e.preventDefault();
    const updatedCV = {
        name: inputCvName.value.trim(),
        email: inputCvEmail.value.trim(),
        branch: inputCvBranch.value.trim().toUpperCase(),
        cgpa: parseFloat(inputCvCgpa.value),
        skills: inputCvSkills.value.trim()
    };
    
    try {
        const response = await fetch('/api/cv', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(updatedCV)
        });
        if (response.ok) {
            renderCV(updatedCV);
            toggleCvEditMode();
        } else {
            alert('Failed to update profile.');
        }
    } catch (e) {
        console.error('Error saving CV:', e);
    }
}

// --- Voice & Text Assistant WebSockets & Recording Logic ---

// --- Voice & Text Assistant WebSockets & Recording Logic ---

function toggleVoiceAssistant() {
    if (isVoiceActive) {
        disconnectVoiceAssistant();
    } else {
        connectVoiceAssistant('voice');
    }
}

function connectVoiceAssistant(mode = 'voice') {
    activeMode = mode;
    console.log(`Connecting WebSocket in ${mode} mode...`);
    
    if (mode === 'voice') {
        btnVoiceToggle.innerText = 'Connecting...';
        btnVoiceToggle.disabled = true;
    }
    
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.host}/ws?mode=${mode}`;
    
    wsConnection = new WebSocket(wsUrl);
    
    wsConnection.onopen = () => {
        console.log("WebSocket connected successfully.");
        isVoiceActive = true;
        
        if (activeMode === 'voice') {
            btnVoiceToggle.innerText = 'Disconnect Coordinator';
            btnVoiceToggle.disabled = false;
            btnVoiceToggle.classList.add('btn-danger');
            btnVoiceToggle.classList.remove('btn-accent');
            assistantStatusText.innerText = 'Connected - Tap Microphone or Type below';
            btnTalk.disabled = false;
        } else {
            assistantStatusText.innerText = 'Text Chat Connected - Type below';
            btnTalk.disabled = true; // Disable microphone in text-only mode
        }
        
        chatLogs.innerHTML = '';
        appendSystemMsg('System: Connected to Placement Assistant WebSocket.');
        
        // Enable Voice & Text controls
        chatTextInput.disabled = false;
        btnSendText.disabled = false;
        
        isRecording = false;
        micContainer.className = 'mic-container';
        
        // If we connected silent-text on first send, dispatch the pending text message now
        if (pendingTextMessage) {
            wsConnection.send(JSON.stringify({
                event: 'user_text',
                text: pendingTextMessage
            }));
            pendingTextMessage = null;
        }
    };
    
    wsConnection.onmessage = async (event) => {
        const data = JSON.parse(event.data);
        
        if (data.event === 'agent_speech') {
            console.log("Received agent speech text:", data.text);
            isAgentSpeaking = true;
            isAgentSending = !!data.stream;
            nextPlayTime = 0;
            
            // Stop any currently playing audio fragments to clear the channel
            stopAllPlayingNodes();
            appendChatMsg('agent', data.text);
            sessionStateBadge.innerText = `State: ${data.state}`;
            
            if (data.audio) {
                // Play standard non-streaming base64 audio directly (REST Response)
                chatTextInput.disabled = true;
                btnSendText.disabled = true;
                btnTalk.disabled = true;
                micContainer.className = 'mic-container speaking';
                assistantStatusText.innerText = 'Coordinator speaking...';
                
                playAudioBuffer(data.audio, () => {
                    isAgentSpeaking = false;
                    micContainer.className = 'mic-container';
                    btnTalk.disabled = false;
                    chatTextInput.disabled = false;
                    btnSendText.disabled = false;
                    assistantStatusText.innerText = 'Ready. Tap to speak or type';
                    if (toggleVad.checked) {
                        startMicStreamAutomatically();
                    }
                });
            } else if (isAgentSending) {
                micContainer.className = 'mic-container speaking';
                btnTalk.disabled = true;
                chatTextInput.disabled = true;
                btnSendText.disabled = true;
                assistantStatusText.innerText = 'Coordinator speaking...';
            } else {
                // Non-streaming / Text-only response (NO Audio playing)
                isAgentSpeaking = false;
                micContainer.className = 'mic-container';
                btnTalk.disabled = (activeMode === 'text');
                chatTextInput.disabled = false;
                btnSendText.disabled = false;
                assistantStatusText.innerText = 'Ready. Tap to speak or type';
            }
        }
        else if (data.event === 'audio_chunk') {
            if (data.audio) {
                playAudioChunk(data.audio);
            }
        }
        else if (data.event === 'audio_end') {
            console.log("TTS stream complete signal received.");
            isAgentSending = false;
            checkAndEnableMicControl();
        }
        else if (data.event === 'user_speech') {
            appendChatMsg('user', data.text);
        }
    };
    
    wsConnection.onerror = (e) => {
        console.error('WS Error:', e);
        appendSystemMsg('System error: WebSocket communication failed.');
    };
    
    wsConnection.onclose = () => {
        console.log("WebSocket connection closed.");
        disconnectVoiceAssistant();
    };
}

function stopAllPlayingNodes() {
    playingSourceNodes.forEach(node => {
        try {
            node.stop();
        } catch (e) {}
    });
    playingSourceNodes = [];
}

function checkAndEnableMicControl() {
    if (!isAgentSending && playingSourceNodes.length === 0) {
        console.log("Playback queue is empty. Enabling inputs...");
        isAgentSpeaking = false;
        micContainer.className = 'mic-container';
        btnTalk.disabled = false;
        chatTextInput.disabled = false;
        btnSendText.disabled = false;
        assistantStatusText.innerText = 'Ready. Tap to speak or type';
        
        if (toggleVad.checked) {
            startMicStreamAutomatically();
        }
    }
}

function disconnectVoiceAssistant() {
    isVoiceActive = false;
    if (isRecording) {
        stopMicStream();
    }
    
    stopAllPlayingNodes();
    visualizeActive = false;
    
    if (wsConnection) {
        if (wsConnection.readyState === WebSocket.OPEN) {
            wsConnection.close();
        }
        wsConnection = null;
    }
    
    btnVoiceToggle.innerText = 'Start Voice Assistant';
    btnVoiceToggle.disabled = false;
    btnVoiceToggle.classList.remove('btn-danger');
    btnVoiceToggle.classList.add('btn-accent');
    
    // Reset inputs, but keep text chat fully active on disconnect
    btnTalk.disabled = true;
    chatTextInput.disabled = false;
    btnSendText.disabled = false;
    chatTextInput.value = '';
    
    micContainer.className = 'mic-container';
    assistantStatusText.innerText = 'Offline - Click Start or Type below to connect';
    sessionStateBadge.innerText = 'State: Offline';
    appendSystemMsg('System: Disconnected.');
}

function resetSession() {
    if (wsConnection && wsConnection.readyState === WebSocket.OPEN) {
        stopAllPlayingNodes();
        visualizeActive = false;
        wsConnection.send(JSON.stringify({ event: 'reset' }));
        appendSystemMsg('System: Resetting session...');
    }
}

// --- Text Messaging Handler (Cost-efficient testing mode) ---
function sendTextMessage() {
    if (isAgentSpeaking) return;
    
    // Abort the microphone stream if active to prevent overlapping stop_recording voice triggers
    if (isRecording) {
        abortMicStream();
    }
    
    const text = chatTextInput.value.trim();
    if (!text) return;
    
    chatTextInput.value = '';
    
    // Instantly append user's text to the chat log
    appendChatMsg('user', text);
    
    // Temporarily lock inputs while waiting for the response
    btnTalk.disabled = true;
    chatTextInput.disabled = true;
    btnSendText.disabled = true;
    assistantStatusText.innerText = 'Processing request...';
    
    // If not connected, dynamically establish a silent text-only WebSocket session
    if (!wsConnection || wsConnection.readyState !== WebSocket.OPEN) {
        pendingTextMessage = text;
        connectVoiceAssistant('text');
    } else {
        wsConnection.send(JSON.stringify({
            event: 'user_text',
            text: text
        }));
    }
}

// Aborts the mic capture stream cleanly without triggering a backend STT transcription
function abortMicStream() {
    if (!isRecording) return;
    isRecording = false;
    silenceStart = null;
    
    micContainer.classList.remove('recording');
    assistantStatusText.innerText = 'Recording cancelled.';
    visualizeActive = false;
    
    if (processorNode) {
        processorNode.disconnect();
        processorNode = null;
    }
    if (micStream) {
        micStream.getTracks().forEach(track => track.stop());
        micStream = null;
    }
    if (audioContext) {
        audioContext.close();
        audioContext = null;
    }
    
    if (wsConnection && wsConnection.readyState === WebSocket.OPEN) {
        wsConnection.send(JSON.stringify({ event: 'cancel_recording' }));
    }
}

// --- Mic Button Handler ---
function handleMicButtonClick() {
    if (!isVoiceActive || isAgentSpeaking) return;
    
    if (isRecording) {
        stopMicStream();
    } else {
        startMicStream();
    }
}

// --- Downsample Helper ---
function downsampleBuffer(buffer, inputSampleRate, outputSampleRate) {
    if (inputSampleRate === outputSampleRate) {
        return buffer;
    }
    const sampleRateRatio = inputSampleRate / outputSampleRate;
    const newLength = Math.round(buffer.length / sampleRateRatio);
    const result = new Float32Array(newLength);
    let offsetResult = 0;
    let offsetBuffer = 0;
    while (offsetResult < result.length) {
        const nextOffsetBuffer = Math.round((offsetResult + 1) * sampleRateRatio);
        let accum = 0, count = 0;
        for (let i = offsetBuffer; i < nextOffsetBuffer && i < buffer.length; i++) {
            accum += buffer[i];
            count++;
        }
        result[offsetResult] = accum / count;
        offsetResult++;
        offsetBuffer = nextOffsetBuffer;
    }
    return result;
}

// --- Audio Capture & Streaming ---

async function startMicStream() {
    if (isRecording || isAgentSpeaking) return;
    isRecording = true;
    silenceStart = null;
    
    stopAllPlayingNodes();
    
    micContainer.classList.add('recording');
    assistantStatusText.innerText = 'Recording... Tap again to send';
    
    try {
        micStream = await navigator.mediaDevices.getUserMedia({ audio: true });
        
        audioContext = new (window.AudioContext || window.webkitAudioContext)();
        const inputSampleRate = audioContext.sampleRate;
        
        const source = audioContext.createMediaStreamSource(micStream);
        
        micAnalyser = audioContext.createAnalyser();
        micAnalyser.fftSize = 256;
        source.connect(micAnalyser);
        
        activeAnalyser = micAnalyser;
        visualizeActive = true;
        drawVisualizer();
        
        processorNode = audioContext.createScriptProcessor(4096, 1, 1);
        
        processorNode.onaudioprocess = (e) => {
            if (!isRecording) return;
            
            const inputData = e.inputBuffer.getChannelData(0);
            const downsampled = downsampleBuffer(inputData, inputSampleRate, 16000);
            
            const int16Buffer = new Int16Array(downsampled.length);
            let sum = 0;
            for (let i = 0; i < downsampled.length; i++) {
                let s = Math.max(-1, Math.min(1, downsampled[i]));
                int16Buffer[i] = s < 0 ? s * 0x8000 : s * 0x7FFF;
                sum += downsampled[i] * downsampled[i];
            }
            
            if (wsConnection && wsConnection.readyState === WebSocket.OPEN) {
                wsConnection.send(int16Buffer.buffer);
            }
            
            const rms = Math.sqrt(sum / downsampled.length);
            if (toggleVad.checked) {
                checkVadSilence(rms);
            }
        };
        
        source.connect(processorNode);
        processorNode.connect(audioContext.destination);
        
    } catch (err) {
        console.error('Failed to capture audio:', err);
        appendSystemMsg('System error: Could not access microphone.');
        stopMicStream();
    }
}

function stopMicStream() {
    if (!isRecording) return;
    isRecording = false;
    silenceStart = null;
    
    micContainer.classList.remove('recording');
    assistantStatusText.innerText = 'Processing speech...';
    
    visualizeActive = false;
    
    if (processorNode) {
        processorNode.disconnect();
        processorNode = null;
    }
    if (micStream) {
        micStream.getTracks().forEach(track => track.stop());
        micStream = null;
    }
    if (audioContext) {
        audioContext.close();
        audioContext = null;
    }
    
    if (wsConnection && wsConnection.readyState === WebSocket.OPEN) {
        wsConnection.send(JSON.stringify({ event: 'stop_recording' }));
    }
}

async function startMicStreamAutomatically() {
    setTimeout(async () => {
        if (!isVoiceActive || isRecording || isAgentSpeaking) return;
        await startMicStream();
    }, 400);
}

function checkVadSilence(rms) {
    if (rms < SILENCE_THRESHOLD) {
        if (!silenceStart) {
            silenceStart = Date.now();
        } else if (Date.now() - silenceStart > SILENCE_DURATION) {
            stopMicStream();
        }
    } else {
        silenceStart = null;
    }
}

// --- Audio Playback & Streaming Queue ---

function base64ToArrayBuffer(base64) {
    const binaryString = window.atob(base64);
    const len = binaryString.length;
    const bytes = new Uint8Array(len);
    for (let i = 0; i < len; i++) {
        bytes[i] = binaryString.charCodeAt(i);
    }
    return bytes.buffer;
}

// Decodes and plays a single block of base64 audio data (REST response)
async function playAudioBuffer(base64String, onEndedCallback) {
    try {
        if (!audioCtx) {
            audioCtx = new (window.AudioContext || window.webkitAudioContext)();
        }
        if (audioCtx.state === 'suspended') {
            await audioCtx.resume();
        }
        
        const arrayBuf = base64ToArrayBuffer(base64String);
        const decodedBuffer = await audioCtx.decodeAudioData(arrayBuf);
        
        const sourceNode = audioCtx.createBufferSource();
        sourceNode.buffer = decodedBuffer;
        
        if (!playbackAnalyser) {
            playbackAnalyser = audioCtx.createAnalyser();
            playbackAnalyser.fftSize = 256;
        }
        
        sourceNode.connect(playbackAnalyser);
        playbackAnalyser.connect(audioCtx.destination);
        
        activeAnalyser = playbackAnalyser;
        visualizeActive = true;
        drawVisualizer();
        
        sourceNode.onended = () => {
            visualizeActive = false;
            playingSourceNodes = playingSourceNodes.filter(n => n !== sourceNode);
            if (onEndedCallback) onEndedCallback();
        };
        
        sourceNode.start(0);
        playingSourceNodes.push(sourceNode);
    } catch (e) {
        console.error("Audio playback error:", e);
        if (onEndedCallback) onEndedCallback();
    }
}

// Schedules continuous chunks back-to-back using AudioContext time
async function playAudioChunk(base64String) {
    try {
        if (!audioCtx) {
            audioCtx = new (window.AudioContext || window.webkitAudioContext)();
        }
        if (audioCtx.state === 'suspended') {
            await audioCtx.resume();
        }
        
        const arrayBuf = base64ToArrayBuffer(base64String);
        const decodedBuffer = await audioCtx.decodeAudioData(arrayBuf);
        const sourceNode = audioCtx.createBufferSource();
        sourceNode.buffer = decodedBuffer;
        
        if (!playbackAnalyser) {
            playbackAnalyser = audioCtx.createAnalyser();
            playbackAnalyser.fftSize = 256;
        }
        
        sourceNode.connect(playbackAnalyser);
        playbackAnalyser.connect(audioCtx.destination);
        
        activeAnalyser = playbackAnalyser;
        visualizeActive = true;
        drawVisualizer();
        
        const currentTime = audioCtx.currentTime;
        if (nextPlayTime < currentTime) {
            nextPlayTime = currentTime;
        }
        
        sourceNode.start(nextPlayTime);
        playingSourceNodes.push(sourceNode);
        
        sourceNode.onended = () => {
            playingSourceNodes = playingSourceNodes.filter(n => n !== sourceNode);
            checkAndEnableMicControl();
        };
        
        nextPlayTime += decodedBuffer.duration;
    } catch (e) {
        console.error("Audio chunk playback error:", e);
    }
}

// --- Canvas Waveform Animation Loops ---

let phase = 0;
function drawAmbientWave() {
    if (visualizeActive) return;
    
    ctx.fillStyle = '#09090e';
    ctx.fillRect(0, 0, visualizerCanvas.width, visualizerCanvas.height);
    
    ctx.lineWidth = 2;
    ctx.strokeStyle = 'rgba(88, 86, 214, 0.3)';
    ctx.beginPath();
    
    const amplitude = 6;
    const frequency = 0.015;
    phase += 0.04;
    
    for (let x = 0; x < visualizerCanvas.width; x++) {
        const y = visualizerCanvas.height / 2 + Math.sin(x * frequency + phase) * amplitude;
        if (x === 0) {
            ctx.moveTo(x, y);
        } else {
            ctx.lineTo(x, y);
        }
    }
    ctx.stroke();
    requestAnimationFrame(drawAmbientWave);
}

function drawVisualizer() {
    if (!visualizeActive || !activeAnalyser) {
        requestAnimationFrame(drawAmbientWave);
        return;
    }
    
    requestAnimationFrame(drawVisualizer);
    
    const bufferLength = activeAnalyser.frequencyBinCount;
    const dataArray = new Uint8Array(bufferLength);
    activeAnalyser.getByteTimeDomainData(dataArray);
    
    ctx.fillStyle = '#09090e';
    ctx.fillRect(0, 0, visualizerCanvas.width, visualizerCanvas.height);
    
    ctx.lineWidth = 3;
    const gradient = ctx.createLinearGradient(0, 0, visualizerCanvas.width, 0);
    
    if (isRecording) {
        gradient.addColorStop(0, '#ff2d55');
        gradient.addColorStop(0.5, '#ff5e7e');
        gradient.addColorStop(1, '#ff2d55');
    } else {
        gradient.addColorStop(0, '#00d2ff');
        gradient.addColorStop(0.5, '#5856d6');
        gradient.addColorStop(1, '#00d2ff');
    }
    
    ctx.strokeStyle = gradient;
    ctx.beginPath();
    
    const sliceWidth = visualizerCanvas.width * 1.0 / bufferLength;
    let x = 0;
    
    for (let i = 0; i < bufferLength; i++) {
        const v = dataArray[i] / 128.0;
        const y = v * visualizerCanvas.height / 2;
        
        if (i === 0) {
            ctx.moveTo(x, y);
        } else {
            ctx.lineTo(x, y);
        }
        
        x += sliceWidth;
    }
    
    ctx.lineTo(visualizerCanvas.width, visualizerCanvas.height / 2);
    ctx.stroke();
}

// --- Chat Logs Helpers ---

function appendChatMsg(sender, text) {
    const bubble = document.createElement('div');
    bubble.className = `chat-bubble ${sender}`;
    bubble.innerText = text;
    chatLogs.appendChild(bubble);
    chatLogs.scrollTop = chatLogs.scrollHeight;
}

function appendSystemMsg(text) {
    const msg = document.createElement('div');
    msg.className = 'system-message';
    msg.innerText = text;
    chatLogs.appendChild(msg);
    chatLogs.scrollTop = chatLogs.scrollHeight;
}
