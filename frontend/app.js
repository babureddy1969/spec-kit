const API_BASE = 'http://localhost:8000';

// Elements
const docListEl = document.getElementById('document-list');
const editorEl = document.getElementById('document-editor');
const titleEl = document.getElementById('editor-title');
const btnSave = document.getElementById('btn-save');
const btnCancel = document.getElementById('btn-cancel');
const spinner = document.getElementById('loading-spinner');
const toastEl = document.getElementById('toast');

// State
let allDocuments = [];
let currentFilename = null;
let originalContent = '';

// Load Documents
async function loadDocuments() {
    try {
        const res = await fetch(`${API_BASE}/documents`);
        const data = await res.json();
        allDocuments = data.documents;
        renderDocumentList();
    } catch (err) {
        showToast('Failed to load documents', 'error');
    }
}

// Render List
function renderDocumentList() {
    docListEl.innerHTML = '';
    allDocuments.forEach(filename => {
        const li = document.createElement('li');
        li.className = `doc-item ${filename === currentFilename ? 'active' : ''}`;
        li.textContent = filename;
        li.onclick = () => selectDocument(filename);
        docListEl.appendChild(li);
    });
}

// Select Document
async function selectDocument(filename) {
    if (currentFilename && editorEl.value !== originalContent) {
        if (!confirm('You have unsaved changes. Discard them?')) return;
    }

    currentFilename = filename;
    renderDocumentList();
    titleEl.textContent = filename;
    
    // Disable UI while loading
    editorEl.disabled = true;
    btnSave.disabled = true;
    btnCancel.disabled = true;
    editorEl.value = 'Loading...';

    try {
        const res = await fetch(`${API_BASE}/documents/${filename}`);
        const data = await res.json();
        originalContent = data.content;
        editorEl.value = originalContent;
        
        // Enable UI
        editorEl.disabled = false;
        btnSave.disabled = false;
        btnCancel.disabled = false;
    } catch (err) {
        showToast('Failed to load file content', 'error');
        editorEl.value = 'Failed to load content.';
    }
}

// Handle Editor Input
editorEl.addEventListener('input', () => {
    // Check if changed to toggle save button state (optional, just keeping it enabled for now once a file is loaded)
});

// Cancel Edits
btnCancel.addEventListener('click', () => {
    if (confirm('Revert all changes?')) {
        editorEl.value = originalContent;
    }
});

// Save Edits & Trigger LLM Sync
btnSave.addEventListener('click', async () => {
    if (!currentFilename) return;

    const newContent = editorEl.value;
    if (newContent === originalContent) {
        showToast('No changes to save.', 'success');
        return;
    }

    // UI Loading state
    btnSave.disabled = true;
    btnCancel.disabled = true;
    editorEl.disabled = true;
    spinner.classList.remove('hidden');
    let oldBtnText = btnSave.textContent;
    btnSave.textContent = 'Syncing...';

    try {
        const res = await fetch(`${API_BASE}/update-doc`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                filename: currentFilename,
                content: newContent
            })
        });

        if (!res.ok) throw new Error('Failed to update document');

        const data = await res.json();
        
        originalContent = newContent; // Mark as saved locally
        
        let msg = `Updated ${currentFilename} successfully.`;
        if (data.updated_documents && data.updated_documents.length > 1) {
            msg += ` Also synced: ${data.updated_documents.filter(d => d !== currentFilename).join(', ')}`;
        }
        
        showToast(msg, 'success');

    } catch (err) {
        showToast(err.message || 'Error occurred during save', 'error');
    } finally {
        btnSave.disabled = false;
        btnCancel.disabled = false;
        editorEl.disabled = false;
        spinner.classList.add('hidden');
        btnSave.textContent = oldBtnText;
    }
});

function showToast(message, type = 'success') {
    toastEl.textContent = message;
    toastEl.className = `toast show ${type}`;
    
    setTimeout(() => {
        toastEl.classList.remove('show');
    }, 5000);
}

// Initialize
loadDocuments();
