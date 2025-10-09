const API_BASE = window.location.origin;

let selectedTemplateId = null;

function switchTab(tabName) {
    const tabs = document.querySelectorAll('.tab-content');
    const buttons = document.querySelectorAll('.tab-btn');
    
    tabs.forEach(tab => tab.classList.remove('active'));
    buttons.forEach(btn => btn.classList.remove('active'));
    
    document.getElementById(tabName).classList.add('active');
    event.target.classList.add('active');
    
    // Load templates when switching to templates tab
    if (tabName === 'templates') {
        loadTemplates();
    }
}

async function loadTemplates() {
    try {
        const response = await fetch(API_BASE + '/api/templates/list');
        const data = await response.json();
        
        if (data.status === 'success') {
            displayTemplates(data.templates);
        } else {
            document.getElementById('template-gallery').innerHTML = '<p>Failed to load templates</p>';
        }
    } catch (error) {
        document.getElementById('template-gallery').innerHTML = '<p>Error loading templates</p>';
    }
}

function displayTemplates(templates) {
    const gallery = document.getElementById('template-gallery');
    gallery.innerHTML = '';
    
    ['female', 'male', 'mixed'].forEach(category => {
        if (templates[category] && templates[category].length > 0) {
            const categoryTitle = document.createElement('h4');
            categoryTitle.textContent = category.charAt(0).toUpperCase() + category.slice(1);
            categoryTitle.style.gridColumn = '1 / -1';
            categoryTitle.style.color = '#667eea';
            categoryTitle.style.marginTop = '10px';
            gallery.appendChild(categoryTitle);
            
            templates[category].forEach(template => {
                const item = document.createElement('div');
                item.className = 'template-item';
                item.onclick = () => selectTemplate(template.id);
                
                item.innerHTML = `
                    <img src="${template.url}" alt="${template.name}">
                    <div class="template-name">${template.name}</div>
                `;
                
                gallery.appendChild(item);
            });
        }
    });
}

function selectTemplate(templateId) {
    selectedTemplateId = templateId;
    
    // Update visual selection
    document.querySelectorAll('.template-item').forEach(item => {
        item.classList.remove('selected');
    });
    event.currentTarget.classList.add('selected');
    
    // Enable swap button if face image is uploaded
    checkSwapReady();
}

// Preview face image
document.addEventListener('DOMContentLoaded', () => {
    const faceInput = document.getElementById('template-face-image');
    if (faceInput) {
        faceInput.addEventListener('change', (e) => {
            const file = e.target.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = (event) => {
                    const preview = document.getElementById('face-preview');
                    preview.innerHTML = `<img src="${event.target.result}" alt="Face preview">`;
                    checkSwapReady();
                };
                reader.readAsDataURL(file);
            }
        });
    }
});

function checkSwapReady() {
    const faceInput = document.getElementById('template-face-image');
    const swapBtn = document.getElementById('swap-btn');
    
    if (selectedTemplateId && faceInput && faceInput.files[0]) {
        swapBtn.disabled = false;
    } else {
        swapBtn.disabled = true;
    }
}

async function swapFaceWithTemplate() {
    const faceInput = document.getElementById('template-face-image');
    
    if (!selectedTemplateId || !faceInput.files[0]) {
        displayResult('template-swap', false, 'Please select a template and upload a face image');
        return;
    }
    
    const formData = new FormData();
    formData.append('face_image', faceInput.files[0]);
    formData.append('template_id', selectedTemplateId);
    
    showLoading(true);
    
    try {
        const response = await fetch(API_BASE + '/api/templates/face-swap', {
            method: 'POST',
            body: formData
        });
        
        if (response.ok) {
            const blob = await response.blob();
            displayResult('template-swap', true, blob);
        } else {
            const error = await response.json();
            displayResult('template-swap', false, error.error || 'Unknown error');
        }
    } catch (error) {
        displayResult('template-swap', false, error.message);
    } finally {
        showLoading(false);
    }
}

function showLoading(show) {
    const loading = document.getElementById('loading');
    if (show) {
        loading.classList.add('show');
    } else {
        loading.classList.remove('show');
    }
}

function displayResult(resultId, success, data) {
    const resultDiv = document.getElementById(resultId + '-result');
    
    if (success) {
        if (data instanceof Blob) {
            const url = URL.createObjectURL(data);
            resultDiv.innerHTML = `
                <div class="success">✅ Success! Image processed</div>
                <img src="${url}" alt="Result">
                <a href="${url}" download="result.png" style="display:inline-block; margin-top:10px; padding:10px; background:#667eea; color:white; text-decoration:none; border-radius:5px;">Download</a>
            `;
        } else {
            resultDiv.innerHTML = `<div class="success">✅ ${data}</div>`;
        }
    } else {
        resultDiv.innerHTML = `<div class="error">❌ Error: ${data}</div>`;
    }
}

async function processImage(feature, endpoint) {
    const fileInput = document.getElementById(feature + '-image');
    
    if (!fileInput || !fileInput.files[0]) {
        displayResult(feature, false, 'Please select an image first');
        return;
    }
    
    const formData = new FormData();
    formData.append('image', fileInput.files[0]);
    
    if (feature === 'hd-upscale') {
        const scale = document.getElementById('hd-scale').value;
        formData.append('scale', scale);
    } else if (feature === 'cartoon') {
        const style = document.getElementById('cartoon-style').value;
        formData.append('style', style);
    } else if (feature === 'style') {
        const style = document.getElementById('art-style').value;
        formData.append('style', style);
    }
    
    showLoading(true);
    
    try {
        const response = await fetch(API_BASE + endpoint, {
            method: 'POST',
            body: formData
        });
        
        if (response.ok) {
            const blob = await response.blob();
            displayResult(feature, true, blob);
        } else {
            const error = await response.json();
            displayResult(feature, false, error.error || 'Unknown error');
        }
    } catch (error) {
        displayResult(feature, false, error.message);
    } finally {
        showLoading(false);
    }
}

async function processFaceSwap() {
    const sourceInput = document.getElementById('face-source');
    const targetInput = document.getElementById('face-target');
    
    if (!sourceInput.files[0] || !targetInput.files[0]) {
        displayResult('faceswap', false, 'Please select both source and target images');
        return;
    }
    
    const formData = new FormData();
    formData.append('source_image', sourceInput.files[0]);
    formData.append('target_image', targetInput.files[0]);
    
    showLoading(true);
    
    try {
        const response = await fetch(API_BASE + '/api/ai/swap-face', {
            method: 'POST',
            body: formData
        });
        
        if (response.ok) {
            const blob = await response.blob();
            displayResult('faceswap', true, blob);
        } else {
            const error = await response.json();
            displayResult('faceswap', false, error.error || 'Unknown error');
        }
    } catch (error) {
        displayResult('faceswap', false, error.message);
    } finally {
        showLoading(false);
    }
}

async function processTextToImage(feature, endpoint) {
    const promptInput = document.getElementById(feature + '-prompt');
    const prompt = promptInput ? promptInput.value : '';
    
    const formData = new FormData();
    if (prompt) {
        formData.append('prompt', prompt);
    }
    
    showLoading(true);
    
    try {
        const response = await fetch(API_BASE + endpoint, {
            method: 'POST',
            body: formData
        });
        
        if (response.ok) {
            const blob = await response.blob();
            displayResult(feature, true, blob);
        } else {
            const error = await response.json();
            displayResult(feature, false, error.error || 'Unknown error');
        }
    } catch (error) {
        displayResult(feature, false, error.message);
    } finally {
        showLoading(false);
    }
}

async function processTemplate() {
    const templateType = document.getElementById('template-type').value;
    
    const formData = new FormData();
    formData.append('template', templateType);
    
    showLoading(true);
    
    try {
        const response = await fetch(API_BASE + '/api/advanced/template-styles', {
            method: 'POST',
            body: formData
        });
        
        if (response.ok) {
            const blob = await response.blob();
            displayResult('template', true, blob);
        } else {
            const error = await response.json();
            displayResult('template', false, error.error || 'Unknown error');
        }
    } catch (error) {
        displayResult('template', false, error.message);
    } finally {
        showLoading(false);
    }
}
