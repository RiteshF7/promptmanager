// Common JavaScript functions shared across pages

const STORAGE_KEY = 'promptManager_prompts';
const DEFAULTS_LOADED_KEY = 'promptManager_defaultsLoaded';
const RECENT_PROMPTS_KEY = 'promptManager_recentUsed';
const MAX_RECENT = 10;

function getStoredPrompts() {
    const stored = localStorage.getItem(STORAGE_KEY);
    return stored ? JSON.parse(stored) : {};
}

function savePrompts(prompts) {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(prompts));
    syncPromptsToServer(prompts);
}

async function syncPromptsToServer(prompts) {
    try {
        const normalized = normalizePromptFormat(prompts);
        await fetch('/api/prompts/sync', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ prompts: normalized })
        });
    } catch (error) {
        console.error('Failed to sync prompts to server:', error);
    }
}

async function loadDefaultPrompts() {
    try {
        const response = await fetch('/api/prompts/defaults');
        return await response.json();
    } catch (error) {
        console.error('Failed to load default prompts:', error);
        return {};
    }
}

function normalizePromptFormat(prompts) {
    const normalized = {};
    for (const [shortcut, data] of Object.entries(prompts)) {
        if (typeof data === 'string') {
            normalized[shortcut] = { text: data, prepend: '', postpend: '' };
        } else {
            normalized[shortcut] = {
                text: data.text || '',
                prepend: data.prepend || '',
                postpend: data.postpend || ''
            };
        }
    }
    return normalized;
}

async function initializePrompts() {
    const defaultsLoaded = localStorage.getItem(DEFAULTS_LOADED_KEY);
    let userPrompts = getStoredPrompts();

    if (!defaultsLoaded) {
        const defaultPrompts = await loadDefaultPrompts();
        const normalizedDefaults = normalizePromptFormat(defaultPrompts);
        const normalizedUser = normalizePromptFormat(userPrompts);
        const mergedPrompts = { ...normalizedDefaults, ...normalizedUser };
        savePrompts(mergedPrompts);
        localStorage.setItem(DEFAULTS_LOADED_KEY, 'true');
        return mergedPrompts;
    }

    userPrompts = normalizePromptFormat(userPrompts);
    savePrompts(userPrompts);
    return userPrompts;
}

function showToast(message, type = 'success') {
    const container = document.getElementById('toast-container');
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.textContent = message;
    container.appendChild(toast);

    toast.offsetHeight;
    toast.classList.add('show');

    setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

async function copyToClipboard(text, shortcut = null) {
    try {
        await navigator.clipboard.writeText(text);
        showToast('Copied to clipboard!');
        if (shortcut) {
            addToRecent(shortcut);
        }
    } catch (err) {
        showToast('Failed to copy', 'error');
    }
}

// Poll for usage tracking from keyboard listener
function startUsageTracking() {
    // Check if there's a way to get usage from server
    // For now, we'll track when users copy prompts
    setInterval(async () => {
        // Could implement server-side tracking here if needed
    }, 5000);
}

function getRecentPrompts() {
    const stored = localStorage.getItem(RECENT_PROMPTS_KEY);
    return stored ? JSON.parse(stored) : [];
}

function addToRecent(shortcut) {
    let recent = getRecentPrompts();
    recent = recent.filter(s => s !== shortcut);
    recent.unshift(shortcut);
    recent = recent.slice(0, MAX_RECENT);
    localStorage.setItem(RECENT_PROMPTS_KEY, JSON.stringify(recent));
}

async function loadSettings() {
    try {
        const response = await fetch('/api/settings');
        const data = await response.json();
        const apiKeyInput = document.getElementById('api-key');
        if (apiKeyInput && data.api_key) {
            apiKeyInput.value = data.api_key;
        }
    } catch (e) {
        console.error("Failed to load settings");
    }
}

