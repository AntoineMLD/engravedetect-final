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
    // Effacer le dessin
    const clearBtn = document.getElementById('clearBtn');
    if (clearBtn) {
        clearBtn.addEventListener('click', clearCanvas);
    }

    // Réinitialiser les tags
    const resetTagsBtn = document.getElementById('resetTagsBtn');
    if (resetTagsBtn) {
        resetTagsBtn.addEventListener('click', resetTags);
    }

    // Ajouter des tags manuellement
    const addManualTagsBtn = document.getElementById('addManualTagsBtn');
    if (addManualTagsBtn) {
        addManualTagsBtn.addEventListener('click', addManualTags);
    }

    // Rechercher les verres correspondants
    const searchVerresBtn = document.getElementById('searchVerresBtn');
    if (searchVerresBtn) {
        searchVerresBtn.addEventListener('click', searchVerres);
    }

    // Fermer la modale (bouton X)
    const closeModalBtn = document.querySelector('#verreModal .close');
    if (closeModalBtn) {
        closeModalBtn.addEventListener('click', closeModal);
    }

    // Actualiser les données (dans le template, à gérer dynamiquement si besoin)
    // document.querySelectorAll('.btn-refresh').forEach(btn => {
    //     btn.addEventListener('click', refreshVerreData);
    // });
    // (À activer si la fonctionnalité est implémentée)
    // Bouton "Rechercher les symboles similaires"
    const searchSymbolsBtn = document.getElementById('searchSymbolsBtn');
    if (searchSymbolsBtn) {
        searchSymbolsBtn.addEventListener('click', searchSimilarSymbols);
    }
    // Formulaire de connexion
    const loginForm = document.getElementById('loginForm');
    if (loginForm) {
        loginForm.addEventListener('submit', handleLogin);
    }
    // Inscription : afficher le formulaire
    const showRegisterLink = document.getElementById('showRegisterLink');
    if (showRegisterLink) {
        showRegisterLink.addEventListener('click', function(e) {
            e.preventDefault();
            document.getElementById('loginForm').classList.add('hidden');
            document.getElementById('registerForm').classList.remove('hidden');
            clearAuthMessages();
            document.getElementById('register-username').focus();
        });
    }

    // Connexion : afficher le formulaire
    const showLoginLink = document.getElementById('showLoginLink');
    if (showLoginLink) {
        showLoginLink.addEventListener('click', function(e) {
            e.preventDefault();
            document.getElementById('registerForm').classList.add('hidden');
            document.getElementById('loginForm').classList.remove('hidden');
            clearAuthMessages();
            document.getElementById('username').focus();
        });
    }

    // Formulaire d'inscription
    const registerForm = document.getElementById('registerForm');
    if (registerForm) {
        registerForm.addEventListener('submit', handleRegister);
    }

    // Bouton de déconnexion
    const logoutBtn = document.getElementById('logoutBtn');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', handleLogout);
    }
}

function clearAuthMessages() {
    const loginError = document.getElementById('loginError');
    const loginSuccess = document.getElementById('loginSuccess');
    const registerError = document.getElementById('registerError');
    const registerSuccess = document.getElementById('registerSuccess');
    if (loginError) loginError.style.display = 'none';
    if (loginSuccess) loginSuccess.style.display = 'none';
    if (registerError) registerError.style.display = 'none';
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
            tagElement.textContent = tag;
            // Ajout du bouton suppression sans inline
            const btn = document.createElement('button');
            btn.className = 'remove-tag';
            btn.textContent = '×';
            btn.addEventListener('click', () => removeTag(tag));
            tagElement.appendChild(btn);
            tagList.appendChild(tagElement);
        });
    }    if (registerSuccess) registerSuccess.style.display = 'none';
}

async function handleRegister(e) {
    e.preventDefault();
    clearAuthMessages();
    const email = document.getElementById('register-email').value.trim();
    const username = document.getElementById('register-username').value.trim();
    const password = document.getElementById('register-password').value;
    const errorDiv = document.getElementById('registerError');
    const successDiv = document.getElementById('registerSuccess');

    if (!email || !username || !password) {
        errorDiv.textContent = 'Veuillez remplir tous les champs.';
        errorDiv.style.display = 'block';
        return;
    }
    // Validation simple email
    if (!/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(email)) {
        errorDiv.textContent = "Adresse email invalide.";
        errorDiv.style.display = 'block';
        return;
    }
    try {
        const response = await fetch(`${API_BASE_URL}/auth/register`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, username, password })
        });
        if (response.ok) {
            successDiv.textContent = "Inscription réussie ! Vous pouvez maintenant vous connecter.";
            successDiv.style.display = 'block';
            // Optionnel : basculer automatiquement sur le login après 2s
            setTimeout(() => {
                document.getElementById('registerForm').classList.add('hidden');
                document.getElementById('loginForm').classList.remove('hidden');
                clearAuthMessages();
                document.getElementById('loginSuccess').textContent = "Compte créé, connectez-vous.";
                document.getElementById('loginSuccess').style.display = 'block';
                document.getElementById('username').focus();
            }, 2000);
        } else {
            const data = await response.json();
            errorDiv.textContent = data.detail || "Erreur lors de l'inscription.";
            errorDiv.style.display = 'block';
        }
    } catch (err) {
        errorDiv.textContent = "Erreur réseau ou serveur.";
        errorDiv.style.display = 'block';
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

    // Support clavier
    canvas.addEventListener('keydown', function(e) {
        if (e.code === 'Space') {
            e.preventDefault();
            clearCanvas();
        }
    });
}

function handleTouch(e) {
    e.preventDefault();
    const touch = e.touches[0];
    const rect = canvas.getBoundingClientRect();
    const x = touch.clientX - rect.left;
    const y = touch.clientY - rect.top;
    
    const mouseEvent = new MouseEvent(e.type === 'touchstart' ? 'mousedown' : 
                                     e.type === 'touchmove' ? 'mousemove' : 'mouseup', {
        clientX: x,
        clientY: y
    });
    
    canvas.dispatchEvent(mouseEvent);
}

function startDrawing(e) {
    isDrawing = true;
    draw(e);
}

function draw(e) {
    if (!isDrawing) return;
    
    const rect = canvas.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;
    
    ctx.lineTo(x, y);
    ctx.stroke();
    ctx.beginPath();
    ctx.moveTo(x, y);
}

function stopDrawing() {
    isDrawing = false;
    ctx.beginPath();
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
        
        const response = await fetch(`${API_IA_BASE_URL}/search_tags`, {
            method: 'POST',
            headers: headers,
            body: JSON.stringify(selectedTags)
        });
        
        if (response.ok) {
            const data = await response.json();
            matchedVerres = data.results || [];
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
        tagElement.textContent = tag;
        // Ajout du bouton suppression sans inline
        const btn = document.createElement('button');
        btn.className = 'remove-tag';
        btn.textContent = '×';
        btn.addEventListener('click', () => removeTag(tag));
        tagElement.appendChild(btn);
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
        const imagePath = `/oversampled_gravures/${className}/${className}.png`;
        html += `
            <div class="result-item">
                <div class="symbol-image">
                    <img src="${imagePath}" alt="${className}" class="result-img">
                    <div class="no-image hidden">Image non trouvée</div>
                </div>
                <div class="symbol-info">
                    <p><strong>Tag :</strong> ${className}</p>
                    <p><strong>Similarité :</strong> ${(similarity * 100).toFixed(1)}%</p>
                    <button class="add-tag-btn" data-class="${className}">Ajouter</button>
                </div>
            </div>
        `;
    });

    html += '</div>';
    resultsContainer.innerHTML = html;

    // Ajout listeners pour les boutons "Ajouter"
    resultsContainer.querySelectorAll('.add-tag-btn').forEach(btn => {
        btn.addEventListener('click', e => {
            const className = btn.getAttribute('data-class');
            addTag(className);
        });
    });
    // Gestion erreur image sans onerror inline
    resultsContainer.querySelectorAll('.result-img').forEach(img => {
        img.addEventListener('error', function() {
            this.style.display = 'none';
            const noImg = this.parentElement.querySelector('.no-image');
            if (noImg) noImg.classList.remove('hidden');
        });
    });
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

    // Filtrer les doublons basés sur le nom et le lien de gravure
    const uniqueVerres = [];
    const seen = new Set();

    matchedVerres.forEach(verre => {
        const nom = verre.nom || 'Non spécifié';
        const gravure = verre.gravure || '';
        const key = `${nom}|${gravure}`;
        if (!seen.has(key)) {
            seen.add(key);
            uniqueVerres.push(verre);
        }
    });

    let html = `<h3>${uniqueVerres.length} verres trouvés (doublons supprimés)</h3>`;
    html += '<div class="verres-list">';

    uniqueVerres.forEach(verre => {
        const nom = verre.nom || 'Non spécifié';
        const fournisseur = verre.fournisseur || 'Non spécifié';
        const variante = verre.variante || '';
        const tags = verre.tags ? verre.tags.join(', ') : '';
        const gravure = verre.gravure || '';
        html += `
            <div class="verre-item">
                <div class="verre-content">
                    <div class="verre-info">
                        <h4>${nom} ${variante}</h4>
                        <p><strong>Fournisseur:</strong> ${fournisseur}</p>
                        <p><strong>Tags:</strong> ${tags}</p>
                        <button class="select-verre-btn" data-id="${verre.id}">Voir détails</button>
                    </div>
                    <div class="verre-gravure">
                        ${gravure ? `<img src="${gravure}" alt="Gravure" class="verre-img">
                        <div class="no-gravure hidden">Gravure non disponible</div>` :
                        '<div class="no-gravure">Aucune gravure</div>'}
                    </div>
                </div>
            </div>
        `;
    });

    html += '</div>';
    verresContainer.innerHTML = html;

    // Ajout listeners pour les boutons "Voir détails"
    verresContainer.querySelectorAll('.select-verre-btn').forEach(btn => {
        btn.addEventListener('click', e => {
            const id = btn.getAttribute('data-id');
            selectVerre(id);
        });
    });
    // Gestion erreur image sans onerror inline
    verresContainer.querySelectorAll('.verre-img').forEach(img => {
        img.addEventListener('error', function() {
            this.style.display = 'none';
            const noImg = this.parentElement.querySelector('.no-gravure');
            if (noImg) noImg.classList.remove('hidden');
        });
    });
}

async function selectVerre(verreId) {
    try {
        const token = localStorage.getItem('access_token');
        const headers = {};
        
        if (token) {
            headers['Authorization'] = `Bearer ${token}`;
        }
        
        const response = await fetch(`${API_IA_BASE_URL}/verre/${verreId}`, {
            headers: headers
        });
        
        if (response.ok) {
            const data = await response.json();
            selectedVerreDetails = data.verre;
            selectedVerreId = verreId;
            updateVerreDetails();
            openModal();
        } else {
            alert('Erreur lors de la récupération des détails du verre');
        }
    } catch (error) {
        console.error('Erreur lors de la sélection du verre:', error);
        alert('Erreur de connexion au serveur');
    }
}

function openModal() {
    const modal = document.getElementById('verreModal');
    if (modal) {
        modal.style.display = 'block';
        modal.setAttribute('aria-hidden', 'false');
        
        // Focus trap pour la modale
        const focusableElements = modal.querySelectorAll(
            'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
        );
        const firstFocusable = focusableElements[0];
        const lastFocusable = focusableElements[focusableElements.length - 1];
        
        // Stocker l'élément qui avait le focus avant l'ouverture
        const previousActiveElement = document.activeElement;
        
        // Focus sur le premier élément
        firstFocusable.focus();
        
        function trapTabKey(e) {
            if (e.key === 'Tab') {
                if (e.shiftKey) {
                    if (document.activeElement === firstFocusable) {
                        e.preventDefault();
                        lastFocusable.focus();
                    }
                } else {
                    if (document.activeElement === lastFocusable) {
                        e.preventDefault();
                        firstFocusable.focus();
                    }
                }
            }
            
            if (e.key === 'Escape') {
                closeModal();
            }
        }
        
        modal.addEventListener('keydown', trapTabKey);
    }
}

function closeModal() {
    const modal = document.getElementById('verreModal');
    if (modal) {
        modal.style.display = 'none';
        modal.setAttribute('aria-hidden', 'true');
        
        // Retourner le focus à l'élément précédent
        if (previousActiveElement) {
            previousActiveElement.focus();
        }
        
        // Supprimer l'event listener du piège à focus
        modal.removeEventListener('keydown', trapTabKey);
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
            <p><strong>Hauteur min:</strong> ${verre.min_hauteur || verre.hauteur_min || 'Non spécifié'}</p>
            <p><strong>Hauteur max:</strong> ${verre.max_hauteur || verre.hauteur_max || 'Non spécifié'}</p>
            <p><strong>Tags:</strong> ${verre.tags ? verre.tags.join(', ') : 'Aucun'}</p>
            ${verre.url_source ? `<p><strong>URL source:</strong> <a href="${verre.url_source}" target="_blank" rel="noopener noreferrer">${verre.url_source}</a></p>` : ''}
        </div>
    `;
    
    detailsContainer.innerHTML = html;
} 