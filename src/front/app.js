console.log("App.js chargé");

// Configuration des URLs API
const API_BASE_URL = 'http://localhost:8000/api/v1';
const API_IA_BASE_URL = 'http://localhost:8001';

// État global de l'application (équivalent session_state de Streamlit)
let isLoggedIn = false;
let currentUser = null;
let canvas = null;
let ctx = null;
let isDrawing = false;
let lastX = 0;
let lastY = 0;
let results = null;
let selectedTags = [];
let matchedVerres = [];
let selectedVerreId = null;
let selectedVerreDetails = null;
let searchPerformed = false;

// Éléments DOM
let loginSection, mainSection, canvasElement, tagInput, tagList, searchResultsContainer;

// Initialisation de l'application
document.addEventListener('DOMContentLoaded', function() {
    initializeElements();
    setupEventListeners();
    checkLoginStatus();
});

function initializeElements() {
    loginSection = document.getElementById('loginSection');
    mainSection = document.getElementById('mainSection');
    canvasElement = document.getElementById('drawingCanvas');
    tagInput = document.getElementById('tagInput');
    tagList = document.getElementById('tagList');
    searchResultsContainer = document.getElementById('searchResults');
    
    // Initialiser le canvas
    if (canvasElement) {
        canvas = canvasElement;
        ctx = canvas.getContext('2d');
        setupCanvas();
    }
}

function setupEventListeners() {
    // Login form
    const loginForm = document.getElementById('loginForm');
    if (loginForm) {
        loginForm.addEventListener('submit', handleLogin);
    }
    
    // Logout button
    const logoutBtn = document.getElementById('logoutBtn');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', handleLogout);
    }
    
    // Clear canvas button
    const clearBtn = document.getElementById('clearBtn');
    if (clearBtn) {
        clearBtn.addEventListener('click', clearCanvas);
    }
    
    // Search similar symbols button
    const searchSymbolsBtn = document.getElementById('searchSymbolsBtn');
    if (searchSymbolsBtn) {
        searchSymbolsBtn.addEventListener('click', searchSimilarSymbols);
    }
    
    // Reset tags button
    const resetTagsBtn = document.getElementById('resetTagsBtn');
    if (resetTagsBtn) {
        resetTagsBtn.addEventListener('click', resetTags);
    }
    
    // Add manual tags button
    const addManualTagsBtn = document.getElementById('addManualTagsBtn');
    if (addManualTagsBtn) {
        addManualTagsBtn.addEventListener('click', addManualTags);
    }
    
    // Search verres button
    const searchVerresBtn = document.getElementById('searchVerresBtn');
    if (searchVerresBtn) {
        searchVerresBtn.addEventListener('click', searchVerres);
    }
}

function setupCanvas() {
    if (!canvas || !ctx) return;
    
    // Définir la taille du canvas (équivalent IMAGE_SIZE = 224)
    canvas.width = 224;
    canvas.height = 224;
    
    // Configuration du contexte (équivalent STROKE_WIDTH = 3)
    ctx.strokeStyle = '#000';
    ctx.lineWidth = 3;
    ctx.lineCap = 'round';
    
    // Ajouter un fond blanc
    ctx.fillStyle = '#FFFFFF';
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    
    // Événements de dessin
    canvas.addEventListener('mousedown', startDrawing);
    canvas.addEventListener('mousemove', draw);
    canvas.addEventListener('mouseup', stopDrawing);
    canvas.addEventListener('mouseout', stopDrawing);
    
    // Support tactile
    canvas.addEventListener('touchstart', handleTouch);
    canvas.addEventListener('touchmove', handleTouch);
    canvas.addEventListener('touchend', stopDrawing);
}

function handleTouch(e) {
    e.preventDefault();
    const touch = e.touches[0];
    const rect = canvas.getBoundingClientRect();
    const x = touch.clientX - rect.left;
    const y = touch.clientY - rect.top;
    
    if (e.type === 'touchstart') {
        startDrawing({ clientX: x, clientY: y });
    } else if (e.type === 'touchmove') {
        draw({ clientX: x, clientY: y });
    }
}

function startDrawing(e) {
    isDrawing = true;
    const rect = canvas.getBoundingClientRect();
    lastX = e.clientX - rect.left;
    lastY = e.clientY - rect.top;
}

function draw(e) {
    if (!isDrawing) return;
    
    const rect = canvas.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;
    
    ctx.beginPath();
    ctx.moveTo(lastX, lastY);
    ctx.lineTo(x, y);
    ctx.stroke();
    
    lastX = x;
    lastY = y;
}

function stopDrawing() {
    isDrawing = false;
}

function clearCanvas() {
    if (!ctx) return;
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    
    // Remettre un fond blanc
    ctx.fillStyle = '#FFFFFF';
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    
    results = null;
    updateUI();
}

async function checkLoginStatus() {
    try {
        const token = localStorage.getItem('access_token');
        if (!token) {
            showLoginInterface();
            return;
        }
        
        // Vérifier si le token n'est pas expiré (simple vérification)
        try {
            const payload = JSON.parse(atob(token.split('.')[1]));
            const now = Math.floor(Date.now() / 1000);
            
            if (payload.exp && payload.exp < now) {
                // Token expiré
                localStorage.removeItem('access_token');
                showLoginInterface();
                return;
            }
            
            // Token valide, afficher l'interface principale
            currentUser = { username: payload.sub || 'utilisateur' };
            isLoggedIn = true;
            showMainInterface();
        } catch (e) {
            // Token invalide
            localStorage.removeItem('access_token');
            showLoginInterface();
        }
    } catch (error) {
        console.error('Erreur lors de la vérification du statut de connexion:', error);
        localStorage.removeItem('access_token');
        showLoginInterface();
    }
}

async function handleLogin(e) {
    e.preventDefault();
    
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;
    
    if (!username || !password) {
        alert('Veuillez remplir tous les champs');
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE_URL}/auth/token`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: `username=${encodeURIComponent(username)}&password=${encodeURIComponent(password)}`
        });
        
        if (response.ok) {
            const data = await response.json();
            // Stocker le token
            localStorage.setItem('access_token', data.access_token);
            currentUser = { username: username };
            isLoggedIn = true;
            showMainInterface();
        } else {
            const error = await response.json();
            alert(`Erreur de connexion: ${error.detail || 'Identifiants incorrects'}`);
        }
    } catch (error) {
        console.error('Erreur lors de la connexion:', error);
        alert('Erreur de connexion au serveur');
    }
}

async function handleLogout() {
    try {
        const token = localStorage.getItem('access_token');
        if (token) {
            await fetch(`${API_BASE_URL}/auth/logout`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });
        }
    } catch (error) {
        console.error('Erreur lors de la déconnexion:', error);
    } finally {
        localStorage.removeItem('access_token');
        isLoggedIn = false;
        currentUser = null;
        resetApplicationState();
        showLoginInterface();
    }
}

function resetApplicationState() {
    results = null;
    selectedTags = [];
    matchedVerres = [];
    selectedVerreId = null;
    selectedVerreDetails = null;
    searchPerformed = false;
    clearCanvas();
}

function showLoginInterface() {
    if (loginSection) loginSection.style.display = 'block';
    if (mainSection) mainSection.style.display = 'none';
}

function showMainInterface() {
    if (loginSection) loginSection.style.display = 'none';
    if (mainSection) mainSection.style.display = 'block';
    
    // Afficher les informations utilisateur
    const userInfo = document.getElementById('userInfo');
    if (userInfo && currentUser) {
        userInfo.textContent = `Connecté en tant que: ${currentUser.username}`;
    }
    
    updateUI();
}

async function searchSimilarSymbols() {
    if (!canvas) {
        alert('Canvas non disponible');
        return;
    }
    
    try {
        // Récupérer le token JWT
        const token = localStorage.getItem('access_token');
        if (!token) {
            alert('Vous devez être connecté pour utiliser cette fonctionnalité');
            return;
        }
        
        // Vérifier si le canvas a du contenu
        const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
        const hasContent = imageData.data.some(pixel => pixel !== 0);
        
        console.log('Canvas contenu vérifié:', {
            width: canvas.width,
            height: canvas.height,
            hasContent: hasContent,
            nonZeroPixels: imageData.data.filter(pixel => pixel !== 0).length
        });
        
        if (!hasContent) {
            alert('Veuillez dessiner quelque chose sur le canvas avant de rechercher');
            return;
        }
        
        // Convertir le canvas en blob
        canvas.toBlob(async (blob) => {
            console.log('Canvas blob créé:', blob);
            console.log('Taille du blob:', blob.size, 'bytes');
            
            const formData = new FormData();
            formData.append('file', blob, 'drawing.png');
            
            console.log('Envoi de la requête vers:', `${API_IA_BASE_URL}/match`);
            
            const response = await fetch(`${API_IA_BASE_URL}/match`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${token}`
                },
                body: formData
            });
            
            if (response.ok) {
                const data = await response.json();
                console.log('Réponse reçue:', data);
                results = data.matches || [];
                updateUI();
            } else {
                const error = await response.json();
                console.error('Erreur API:', error);
                alert(`Erreur API : ${error.detail || 'Erreur inconnue'}`);
            }
        }, 'image/png');
        
    } catch (error) {
        console.error('Erreur lors de la recherche de symboles:', error);
        alert('Erreur de connexion au serveur');
    }
}

function addTag(tagName) {
    if (!selectedTags.includes(tagName)) {
        selectedTags.push(tagName);
        updateUI();
    }
}

function removeTag(tagToRemove) {
    selectedTags = selectedTags.filter(tag => tag !== tagToRemove);
    updateUI();
}

function resetTags() {
    selectedTags = [];
    matchedVerres = [];
    searchPerformed = false;
    updateUI();
}

function addManualTags() {
    const manualInput = document.getElementById('manualInput');
    if (!manualInput) return;
    
    const input = manualInput.value.trim();
    if (!input) return;
    
    // Si l'entrée contient des virgules, la diviser en tags séparés
    let manualTags = [];
    if (input.includes(',')) {
        manualTags = input.split(',').map(t => t.trim()).filter(t => t);
    } else {
        manualTags = [input];
    }
    
    // Ajouter les nouveaux tags
    manualTags.forEach(tag => {
        if (!selectedTags.includes(tag)) {
            selectedTags.push(tag);
        }
    });
    
    manualInput.value = '';
    updateUI();
}

async function searchVerres() {
    if (selectedTags.length === 0) {
        alert('Veuillez ajouter au moins un tag avant de rechercher');
        return;
    }
    
    try {
        const token = localStorage.getItem('access_token');
        const headers = {
            'Content-Type': 'application/json',
        };
        
        if (token) {
            headers['Authorization'] = `Bearer ${token}`;
        }
        
        const response = await fetch(`${API_BASE_URL}/verres/search`, {
            method: 'POST',
            headers: headers,
            credentials: 'include',
            body: JSON.stringify({
                tags: selectedTags
            })
        });
        
        if (response.ok) {
            matchedVerres = await response.json();
            searchPerformed = true;
            updateUI();
        } else {
            const error = await response.json();
            alert(`Erreur API : ${error.detail || 'Erreur inconnue'}`);
        }
    } catch (error) {
        console.error('Erreur lors de la recherche de verres:', error);
        alert('Erreur de connexion au serveur');
    }
}

function updateUI() {
    updateTagsDisplay();
    updateResultsDisplay();
    updateVerresDisplay();
}

function updateTagsDisplay() {
    if (!tagList) return;
    
    tagList.innerHTML = '';
    if (selectedTags.length === 0) {
        tagList.innerHTML = '<p>Aucun tag sélectionné.</p>';
        return;
    }
    
    selectedTags.forEach(tag => {
        const tagElement = document.createElement('span');
        tagElement.className = 'tag';
        tagElement.innerHTML = `
            ${tag}
            <button onclick="removeTag('${tag}')" class="remove-tag">×</button>
        `;
        tagList.appendChild(tagElement);
    });
}

function updateResultsDisplay() {
    const resultsContainer = document.getElementById('resultsContainer');
    if (!resultsContainer) return;
    
    if (!results) {
        resultsContainer.innerHTML = '';
        return;
    }
    
    const NUM_RESULTS = 10;
    let html = `<h3>Top ${NUM_RESULTS} symboles similaires trouvés</h3>`;
    html += '<div class="results-grid">';
    
    results.slice(0, NUM_RESULTS).forEach((res, idx) => {
        const className = res.class_ || res.class || 'inconnu';
        const similarity = res.similarity || 0.0;
        
        // Nouveau chemin d'accès aux images
        const imagePath = `/oversampled_gravures/${className}/${className}.png`;
        
        html += `
            <div class="result-item">
                <div class="symbol-image">
                    <img src="${imagePath}" alt="${className}" onerror="this.style.display='none'; this.nextElementSibling.style.display='block';">
                    <div class="no-image" style="display: none; color: #999; font-size: 12px;">Image non trouvée</div>
                </div>
                <div class="symbol-info">
                    <p><strong>Tag :</strong> ${className}</p>
                    <p><strong>Similarité :</strong> ${(similarity * 100).toFixed(1)}%</p>
                    <button onclick="addTag('${className}')" class="add-tag-btn">Ajouter</button>
                </div>
            </div>
        `;
    });
    
    html += '</div>';
    resultsContainer.innerHTML = html;
}

function updateVerresDisplay() {
    const verresContainer = document.getElementById('verresContainer');
    if (!verresContainer) return;
    
    if (!searchPerformed) {
        verresContainer.innerHTML = '<p>Recherchez des verres pour afficher les résultats.</p>';
        return;
    }
    
    if (matchedVerres.length === 0) {
        verresContainer.innerHTML = '<p>Aucun verre ne correspond aux tags.</p>';
        return;
    }
    
    let html = `<h3>${matchedVerres.length} verres trouvés</h3>`;
    html += '<div class="verres-list">';
    
    matchedVerres.forEach(verre => {
        const nom = verre.nom || 'Non spécifié';
        const fournisseur = verre.fournisseur || 'Non spécifié';
        const variante = verre.variante || '';
        const tags = verre.tags ? verre.tags.join(', ') : '';
        
        html += `
            <div class="verre-item">
                <h4>${nom} ${variante}</h4>
                <p><strong>Fournisseur:</strong> ${fournisseur}</p>
                <p><strong>Tags:</strong> ${tags}</p>
                <button onclick="selectVerre(${verre.id})" class="select-verre-btn">Voir détails</button>
            </div>
        `;
    });
    
    html += '</div>';
    verresContainer.innerHTML = html;
}

async function selectVerre(verreId) {
    try {
        const token = localStorage.getItem('access_token');
        const headers = {};
        
        if (token) {
            headers['Authorization'] = `Bearer ${token}`;
        }
        
        const response = await fetch(`${API_BASE_URL}/verres/${verreId}`, {
            headers: headers,
            credentials: 'include'
        });
        
        if (response.ok) {
            selectedVerreDetails = await response.json();
            selectedVerreId = verreId;
            updateVerreDetails();
        } else {
            alert('Erreur lors de la récupération des détails du verre');
        }
    } catch (error) {
        console.error('Erreur lors de la sélection du verre:', error);
        alert('Erreur de connexion au serveur');
    }
}

function updateVerreDetails() {
    const detailsContainer = document.getElementById('verreDetailsContainer');
    if (!detailsContainer || !selectedVerreDetails) return;
    
    const verre = selectedVerreDetails;
    let html = '<h3>Détails du verre sélectionné</h3>';
    
    html += `
        <div class="verre-details">
            <h4>${verre.nom || 'Non spécifié'} ${verre.variante || ''}</h4>
            <p><strong>ID:</strong> ${verre.id}</p>
            <p><strong>Fournisseur:</strong> ${verre.fournisseur || 'Non spécifié'}</p>
            <p><strong>Indice:</strong> ${verre.indice || 'Non spécifié'}</p>
            <p><strong>Tags:</strong> ${verre.tags ? verre.tags.join(', ') : 'Aucun'}</p>
        </div>
    `;
    
    detailsContainer.innerHTML = html;
} 