// src/front/api.js

// Utiliser les URLs qui fonctionnent dans Docker
const API_URL = 'http://localhost:8000/api/v1';
const API_IA_URL = 'http://localhost:8001';
const REF_IMG_DIR = '/data/oversampled_gravures';

// Fonction pour obtenir le token d'authentification
function getToken() {
    return localStorage.getItem('token');
}

// Fonction pour définir le token d'authentification
function setToken(token) {
    localStorage.setItem('token', token);
}

// Fonction pour supprimer le token d'authentification
function removeToken() {
    localStorage.removeItem('token');
}

// Fonction de connexion
export async function login(email, password) {
    try {
        const formData = new URLSearchParams();
        formData.append('username', email);
        formData.append('password', password);

        const response = await fetch(`${API_URL}/auth/token`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
                'Accept': 'application/json'
            },
            body: formData
        });

        if (!response.ok) {
            const errorData = await response.json().catch(() => null);
            throw new Error(errorData?.detail || `Erreur HTTP: ${response.status}`);
        }

        const data = await response.json();
        setToken(data.access_token);
        return data;
    } catch (error) {
        console.error('Erreur de connexion:', error);
        throw error;
    }
}

// Fonction de déconnexion
export function logout() {
    removeToken();
}

// Fonction pour obtenir des tags similaires
export async function getSimilarTags(imageData) {
    try {
        const token = getToken();
        if (!token) throw new Error('Non authentifié');

        const response = await fetch(`${API_IA_URL}/match`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ image: imageData })
        });

        if (!response.ok) {
            throw new Error(`Erreur HTTP: ${response.status}`);
        }

        return await response.json();
    } catch (error) {
        console.error('Erreur lors de la recherche de tags similaires:', error);
        throw error;
    }
}

// Fonction pour valider une prédiction
export async function validatePrediction(className) {
    try {
        const token = getToken();
        if (!token) throw new Error('Non authentifié');

        const response = await fetch(`${API_IA_URL}/validate`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ class_name: className })
        });

        if (!response.ok) {
            throw new Error(`Erreur HTTP: ${response.status}`);
        }

        return await response.json();
    } catch (error) {
        console.error('Erreur lors de la validation:', error);
        throw error;
    }
}

// Fonction pour rechercher des verres par tags
export async function searchVerresByTags(tags) {
    try {
        const token = getToken();
        if (!token) throw new Error('Non authentifié');

        const response = await fetch(`${API_URL}/verres/search`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ tags })
        });

        if (!response.ok) {
            throw new Error(`Erreur HTTP: ${response.status}`);
        }

        return await response.json();
    } catch (error) {
        console.error('Erreur lors de la recherche de verres:', error);
        throw error;
    }
}

// Fonction pour obtenir les détails d'un verre
export async function getFullVerreDetails(verreId) {
    try {
        const token = getToken();
        if (!token) throw new Error('Non authentifié');

        // Récupérer les détails de base
        const detailsResponse = await fetch(`${API_URL}/verres/${verreId}`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        if (!detailsResponse.ok) {
            throw new Error(`Erreur HTTP: ${detailsResponse.status}`);
        }

        const verreDetails = await detailsResponse.json();

        // Récupérer les détails de staging
        try {
            const stagingResponse = await fetch(`${API_URL}/verres/${verreId}/staging`, {
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });

            if (stagingResponse.ok) {
                const stagingDetails = await stagingResponse.json();
                // Fusionner les détails de staging avec les détails de base
                Object.assign(verreDetails, stagingDetails);
            }
        } catch (error) {
            console.warn(`Impossible de récupérer les détails de staging pour le verre ${verreId}:`, error);
        }

        return verreDetails;
    } catch (error) {
        console.error('Erreur lors de la récupération des détails du verre:', error);
        throw error;
    }
}

// Fonction pour trouver une image de symbole
export async function findSymbolImage(symbolName) {
    if (!symbolName || symbolName.toLowerCase() === 'inconnu') {
        console.warn(`Nom de symbole invalide: ${symbolName}`);
        return null;
    }

    const token = getToken();
    if (!token) throw new Error('Non authentifié');

    try {
        const response = await fetch(`${API_URL}/symbols/${symbolName}/image`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        if (!response.ok) {
            throw new Error(`Erreur HTTP: ${response.status}`);
        }

        const data = await response.json();
        return data.image_url;
    } catch (error) {
        console.error('Erreur lors de la recherche de l\'image du symbole:', error);
        return null;
    }
}

// Fonction pour obtenir les détails d'un verre
export async function getGlassDetails(gravure) {
    return await fetchWithAuth(`${API_URL}/verres/search?gravure=${encodeURIComponent(gravure)}`);
}

// Fonction utilitaire pour les appels API
async function fetchWithAuth(url, options = {}) {
    if (getToken()) {
        options.headers = {
            ...options.headers,
            "Authorization": `Bearer ${getToken()}`
        };
    }
    const response = await fetch(url, options);
    if (!response.ok) {
        const error = await response.text();
        throw new Error(error);
    }
    return response.json();
}
