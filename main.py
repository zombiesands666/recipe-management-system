import streamlit as st
from database import (
    init_db, get_categories, add_recipe, get_recipes,
    get_recipe, get_recipe_ingredients
)
import os
from streamlit.components.v1 import html

# Initialize the database
try:
    init_db()
except Exception as e:
    st.error(f"Database initialization failed: {e}")

# Configure the page
st.set_page_config(
    page_title="Recipe Management System",
    page_icon="🍳",
    layout="wide"
)

# Custom CSS for mobile responsiveness and bottom navigation
st.markdown("""
<style>
    /* General mobile optimizations */
    .stButton > button {
        width: 100%;
        min-height: 44px; /* Better touch targets */
    }
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea {
        font-size: 16px !important;
    }
    
    /* Bottom navigation bar for mobile */
    @media (max-width: 768px) {
        .bottom-nav {
            position: fixed;
            bottom: 0;
            left: 0;
            right: 0;
            background: white;
            display: flex;
            justify-content: space-around;
            padding: 10px;
            box-shadow: 0 -2px 5px rgba(0,0,0,0.1);
            z-index: 1000;
        }
        .bottom-nav a {
            text-decoration: none;
            color: #262730;
            padding: 8px 12px;
            border-radius: 5px;
            display: flex;
            flex-direction: column;
            align-items: center;
            font-size: 12px;
        }
        .bottom-nav a.active {
            background-color: #f63366;
            color: white;
        }
        /* Add padding to main content to prevent overlap with bottom nav */
        .main-content {
            padding-bottom: 70px;
        }
        .row-widget.stButton {
            margin: 5px 0;
        }
        .stMarkdown {
            font-size: 14px;
        }
    }
    
    /* PWA Install prompt styling */
    #pwa-install {
        background-color: #f63366;
        color: white;
        padding: 15px;
        border-radius: 10px;
        margin-bottom: 20px;
        text-align: center;
        box-shadow: 0 2px 5px rgba(0,0,0,0.2);
    }
    #pwa-install button {
        background-color: white;
        color: #f63366;
        border: none;
        padding: 12px 24px;
        border-radius: 5px;
        cursor: pointer;
        font-weight: bold;
        margin-top: 10px;
        font-size: 16px;
        transition: all 0.3s ease;
    }
    #pwa-install button:hover {
        transform: translateY(-2px);
        box-shadow: 0 2px 5px rgba(0,0,0,0.2);
    }
    
    /* Offline status indicator */
    #offline-status {
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        background-color: #ff4b4b;
        color: white;
        text-align: center;
        padding: 5px;
        z-index: 1000;
        display: none;
    }
    
    /* Recipe card improvements */
    .recipe-card {
        border: 1px solid #e0e0e0;
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 15px;
        transition: transform 0.3s ease;
        cursor: pointer;
        touch-action: pan-y pinch-zoom;
    }
    .recipe-card:hover {
        transform: translateY(-2px);
    }
</style>

<div id="offline-status">
    You are currently offline. Changes will be synced when you're back online.
</div>
""", unsafe_allow_html=True)

# Enhanced PWA install prompt with platform-specific instructions
install_prompt = """
<div id="pwa-install" style="display: none;">
    <h3 style="margin: 0;">📱 Install Recipe App</h3>
    <p style="margin: 10px 0;">Get the best experience with our app!</p>
    <div id="install-instructions" style="font-size: 14px; margin: 10px 0;">
        <!-- Instructions will be inserted here by JavaScript -->
    </div>
    <button onclick="installPWA()" id="install-button">Install App</button>
</div>

<script>
let deferredPrompt;
const installDiv = document.getElementById('pwa-install');
const instructionsDiv = document.getElementById('install-instructions');
const installButton = document.getElementById('install-button');

// Platform-specific instructions
function updateInstallInstructions() {
    const ua = navigator.userAgent;
    let instructions = '';
    
    if (/iPhone|iPad|iPod/.test(ua)) {
        instructions = '1. Tap the share button (📤)<br>2. Scroll down and tap "Add to Home Screen"';
        installButton.style.display = 'none';
    } else if (/Android/.test(ua)) {
        instructions = 'Tap "Install App" when prompted';
    } else {
        instructions = 'Click "Install App" to add to your desktop';
    }
    instructionsDiv.innerHTML = instructions;
}

// Check online status and update UI
function updateOnlineStatus() {
    const offlineStatus = document.getElementById('offline-status');
    if (navigator.onLine) {
        offlineStatus.style.display = 'none';
    } else {
        offlineStatus.style.display = 'block';
    }
}

window.addEventListener('online', updateOnlineStatus);
window.addEventListener('offline', updateOnlineStatus);

// PWA installation
window.addEventListener('beforeinstallprompt', (e) => {
    e.preventDefault();
    deferredPrompt = e;
    installDiv.style.display = 'block';
    updateInstallInstructions();
});

function installPWA() {
    if (deferredPrompt) {
        deferredPrompt.prompt();
        deferredPrompt.userChoice.then((choiceResult) => {
            if (choiceResult.outcome === 'accepted') {
                console.log('User accepted the install prompt');
            }
            deferredPrompt = null;
            installDiv.style.display = 'none';
        });
    }
}

// Register service worker
if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
        navigator.serviceWorker.register('/static/service-worker.js')
            .then(registration => {
                console.log('ServiceWorker registration successful');
            })
            .catch(error => {
                console.error('ServiceWorker registration failed:', error);
            });
    });
}

// Add touch event listeners for swipe gestures on recipe cards
document.addEventListener('DOMContentLoaded', () => {
    let touchStartX = 0;
    let touchEndX = 0;
    
    const cards = document.querySelectorAll('.recipe-card');
    cards.forEach(card => {
        card.addEventListener('touchstart', e => {
            touchStartX = e.changedTouches[0].screenX;
        });
        
        card.addEventListener('touchend', e => {
            touchEndX = e.changedTouches[0].screenX;
            handleSwipe(card);
        });
    });
    
    function handleSwipe(card) {
        const swipeThreshold = 50;
        const diff = touchEndX - touchStartX;
        
        if (Math.abs(diff) > swipeThreshold) {
            if (diff > 0) {
                // Swipe right - favorite recipe
                card.classList.add('favorited');
            } else {
                // Swipe left - hide recipe
                card.style.display = 'none';
            }
        }
    }
});
</script>
"""

# Add the install prompt to the sidebar at the top
st.sidebar.markdown(install_prompt, unsafe_allow_html=True)

# Rest of your Streamlit app code remains the same...
# (Previous code for recipe management functionality)

# Add bottom navigation for mobile
bottom_nav = """
<div class="bottom-nav">
    <a href="?page=View+Recipes" class="nav-item">
        📖<br>Recipes
    </a>
    <a href="?page=Add+New+Recipe" class="nav-item">
        ➕<br>Add Recipe
    </a>
</div>
"""

# Add bottom navigation at the end of the page
st.markdown(bottom_nav, unsafe_allow_html=True)
