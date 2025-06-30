import os
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

import streamlit as st
import numpy as np
import json
import faiss
import requests
from PIL import Image
from transformers import CLIPProcessor, CLIPModel
import random
import base64
from io import BytesIO

# Set page config
st.set_page_config(
    page_title="Pic2Pick", 
    page_icon="🛍️", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Enhanced CSS with background image and hover effects
st.markdown("""

<style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');
    @import url('https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css');
    @import url('https://fonts.googleapis.com/css2?family=Russo+One&family=Orbitron:wght@400;700;900&family=Exo+2:wght@400;600;700&family=Rajdhani:wght@400;600;700&family=Libertinus+Math&family=Fredericka+the+Great&family=Bebas+Neue&family=Audiowide&family=Electrolize&display=swap');       
    
    /* COMPLETE HORIZONTAL SCROLL PREVENTION */
    html {
        overflow-x: hidden !important;
        max-width: 100vw !important;
        width: 100vw !important;
    }
    
    body {
        overflow-x: hidden !important;
        max-width: 100vw !important;
        width: 100vw !important;
        margin: 0 !important;
        padding: 0 !important;
    }
    
    * {
        box-sizing: border-box !important;
        max-width: 100% !important;
    }
    
    .stApp, .stApp > div, .main, .main > div {
        overflow-x: hidden !important;
        max-width: 100vw !important;
        width: 100% !important;
    }

    /* Deep background with white dots */
    .stApp {
        background: #053336;
        font-family: 'Inter', sans-serif;
        position: relative;
        overflow-x: hidden !important;
        max-width: 100vw !important;
        width: 100vw !important;
        min-height: 100vh;
    }

    /* White dots pattern - static */
    .stApp::before {
        content: '';
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background-image: 
            radial-gradient(circle at 1px 1px, rgba(255, 255, 255, 0.9) 0.5px, rgba(255, 255, 255, 0.3) 1px, transparent 1.5px);
        background-size: 30px 30px;
        opacity: 0.6;
        z-index: -1;
    }

    /* Ensure Streamlit content appears above background */
    .stApp > div {
        position: relative;
        z-index: 1;
    }

    
/* Main container adjustments */
.main .block-container {
    padding-top: 1rem;
    padding-bottom: 2rem;
    padding-left: 1rem;
    padding-right: 1rem;
    background: rgba(15, 23, 42, 0.75);
    backdrop-filter: blur(15px);
    border-radius: 25px;
    margin-top: 1rem;
    border: 1px solid rgba(255, 255, 255, 0.1);
    box-shadow: 
        0 25px 50px rgba(0, 0, 0, 0.3),
        0 0 0 1px rgba(255, 255, 255, 0.05);
    animation: containerFloat 12s ease-in-out infinite;
    max-width: 100% !important;
    overflow-x: hidden !important;
    position: relative;
}

@keyframes containerFloat {
    0%, 100% { transform: translateY(0px) rotateX(0deg); }
    50% { transform: translateY(-5px) rotateX(0.5deg); }
}

/* Top bar for input method selector - moved to topmost right */
.top-bar {
    position: fixed;
    top: 0.5rem;
    right: 0.5rem;
    z-index: 20;
    background: rgba(0, 0, 0, 0.8);
    backdrop-filter: blur(10px);
    border: 1px solid rgba(255, 255, 255, 0.15);
    border-radius: 15px;
    padding: 0.75rem 1rem;
    animation: slideInFromRight 1s ease-out;
}

@keyframes slideInFromRight {
    from { opacity: 0; transform: translateX(100px); }
    to { opacity: 1; transform: translateX(0); }
}

/* Header section styling */
.header-section {
    text-align: left;
    margin-bottom: 1rem;
    margin-top: 0.5rem;
    animation: slideInLeft 1s ease-out;
    position: relative;
}

@keyframes slideInLeft {
    from { opacity: 0; transform: translateX(-50px); }
    to { opacity: 1; transform: translateX(0); }
}

/* Title styling with shopping cart icon - Bold white with cool font */
.main-title {
    color: #ffffff !important;
    font-family: 'Audiowide', 'Orbitron', 'Electrolize', 'Bebas Neue', sans-serif !important;
    font-weight: 900 !important;
    font-size: 5rem !important;
    margin-bottom: 0.5rem !important;
    display: flex;
    align-items: center;
    gap: 1.5rem;
    text-shadow: 3px 3px 12px rgba(0, 0, 0, 0.8);
    letter-spacing: 0.08em;
    text-transform: uppercase;
}

.title-icon {
    font-size: 4rem;
    color: #ffffff;
    font-weight: 900;
    filter: drop-shadow(3px 3px 12px rgba(0, 0, 0, 0.8));
}

/* Tagline styling - Bold white color with cool font */
.tagline {
    color: #ffffff !important;
    font-family: 'Electrolize', 'Audiowide', 'Orbitron', 'Bebas Neue', sans-serif !important;
    font-size: 2rem !important;
    font-weight: 900 !important;
    margin-bottom: 1rem !important;
    letter-spacing: 0.2em !important;
    word-spacing: 0.4em !important;
    animation: fadeInUp 1.5s ease-out 0.5s both;
    text-transform: uppercase;
    text-shadow: 2px 2px 8px rgba(0, 0, 0, 0.8);
    background: none !important;
}

@keyframes fadeInUp {
    from { opacity: 0; transform: translateY(20px); }
    to { opacity: 1; transform: translateY(0); }
}

/* About section styling - Black text with Libertinus Math font and glass background */
.about-section {
    color: #000000 !important;
    font-family: 'Libertinus Math', serif !important;
    font-size: 1.2rem !important;
    line-height: 1.8 !important;
    margin-bottom: 2rem !important;
    animation: fadeInUp 1.5s ease-out 1s both;
    background: rgba(255, 255, 255, 0.12) !important;
    backdrop-filter: blur(25px) !important;
    -webkit-backdrop-filter: blur(25px) !important;
    padding: 2rem;
    border-radius: 20px;
    border: 1px solid rgba(255, 255, 255, 0.18);
    box-shadow: 
        0 8px 32px rgba(0, 0, 0, 0.15),
        inset 0 1px 0 rgba(255, 255, 255, 0.25);
    font-weight: 600;
    text-shadow: 0 1px 2px rgba(255, 255, 255, 0.3);
    position: relative;
    overflow: hidden;
}

.about-section::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: linear-gradient(135deg, 
        rgba(255, 255, 255, 0.1) 0%, 
        rgba(255, 255, 255, 0.05) 50%, 
        rgba(255, 255, 255, 0.1) 100%);
    pointer-events: none;
    border-radius: 20px;
}

.about-section > * {
    position: relative;
    z-index: 1;
}

/* File upload section - positioned next to about */
.upload-section-inline {
    display: flex;
    gap: 2rem;
    align-items: flex-start;
    margin-bottom: 3rem;
    animation: slideInUp 1.5s ease-out 1.2s both;
}

@keyframes slideInUp {
    from { opacity: 0; transform: translateY(30px); }
    to { opacity: 1; transform: translateY(0); }
}

.about-content {
    flex: 1;
}
    .upload-content {
        flex: 1;
        min-width: 300px;
    }
    
    /* Enhanced file uploader - removed animation and hover effects */
    .stFileUploader {
        background: rgba(0, 0, 0, 0.6) !important;
        border: 2px dashed rgba(59, 130, 246, 0.5);
        border-radius: 20px;
        padding: 2rem;
        text-align: center;
        transition: all 0.4s ease;
        width: 100% !important;
        max-width: 100% !important;
        box-sizing: border-box !important;
        backdrop-filter: blur(10px);
        position: relative;
        overflow: hidden;
        box-shadow: 0 0 25px rgba(59, 130, 246, 0.2);
    }
    
    .stFileUploader:hover {
        border-color: rgba(59, 130, 246, 0.8);
        background: rgba(0, 0, 0, 0.8) !important;
        transform: translateY(-5px) scale(1.03);
        box-shadow: 0 15px 40px rgba(59, 130, 246, 0.3);
    }
    
    .stFileUploader label {
        color: #ffffff !important;
        font-size: 1.1rem !important;
        font-weight: 600 !important;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 0.75rem;
        text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.5);
    }

    .stFileUploader label::before {
        content: '\f07c';
        font-family: 'Font Awesome 6 Free';
        font-weight: 900;
        font-size: 1.5rem;
        color: #3b82f6;
    }
    
    /* Product boxes */
    .product-box {
        background: rgba(0, 0, 0, 0.7) !important;
        border: 2px solid rgba(59, 130, 246, 0.3);
        border-radius: 20px;
        padding: 2rem;
        margin-bottom: 3rem;
        height: 450px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        transition: all 0.4s ease;
        backdrop-filter: blur(15px);
        animation: productFloat 8s ease-in-out infinite;
        position: relative;
        box-shadow: 
            0 10px 30px rgba(0, 0, 0, 0.5),
            0 0 0 1px rgba(255, 255, 255, 0.05);
        width: 100% !important;
        max-width: 100% !important;
        box-sizing: border-box !important;
        overflow: hidden;
    }

    .product-box::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.05), transparent);
        transition: left 0.7s;
    }

    .product-box:hover::before {
        left: 100%;
    }
    
    @keyframes productFloat {
        0%, 100% { transform: translateY(0px) rotateY(0deg); }
        50% { transform: translateY(-3px) rotateY(1deg); }
    }
    
    .product-box:hover {
        transform: translateY(-12px) scale(1.03) rotateY(2deg);
        box-shadow: 
            0 20px 50px rgba(59, 130, 246, 0.25),
            0 0 30px rgba(59, 130, 246, 0.15);
        border-color: rgba(59, 130, 246, 0.6);
        background: rgba(15, 15, 15, 0.9) !important;
        animation-play-state: paused;
    }
    
    /* Product header */
    .product-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 1rem;
        color: #ffffff;
        font-weight: 600;
        font-size: 0.95rem;
    }
    
    .product-title {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.5);
    }
    
    .similarity-badge-header {
        background: linear-gradient(135deg, #3b82f6, #1d4ed8);
        color: white;
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 700;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(59, 130, 246, 0.3);
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .product-box:hover .similarity-badge-header {
        transform: scale(1.1) rotate(-2deg);
        box-shadow: 0 6px 20px rgba(59, 130, 246, 0.5);
    }
    
    .product-image-container {
        height: 240px;
        display: flex;
        align-items: center;
        justify-content: center;
        overflow: hidden;
        border-radius: 15px;
        background: rgba(0, 0, 0, 0.8) !important;
        margin-bottom: 1.5rem;
        transition: all 0.4s ease;
        border: 1px solid rgba(59, 130, 246, 0.2);
        position: relative;
    }

    .product-image-container::after {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: linear-gradient(45deg, transparent 30%, rgba(255, 255, 255, 0.03) 50%, transparent 70%);
        opacity: 0;
        transition: opacity 0.3s ease;
    }

    .product-box:hover .product-image-container::after {
        opacity: 1;
    }
    
    .product-box:hover .product-image-container {
        background: rgba(10, 10, 10, 0.9) !important;
        transform: scale(1.03) rotateX(2deg);
        border-color: rgba(59, 130, 246, 0.4);
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.3);
    }
    
    .product-image-container img {
        max-width: 100%;
        max-height: 100%;
        object-fit: contain;
        border-radius: 10px;
        transition: all 0.4s ease;
        filter: brightness(1.1) contrast(1.1);
    }

    .product-box:hover .product-image-container img {
        transform: scale(1.05);
        filter: brightness(1.2) contrast(1.2);
    }
    
    .product-info {
        text-align: center;
        margin-top: auto;
    }
    
    .price-tag {
        color: #fbbf24;
        font-size: 1.2rem;
        font-weight: 700;
        margin: 0.5rem 0;
        transition: all 0.3s ease;
        text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.5);
        background: linear-gradient(45deg, #fbbf24, #f59e0b);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    .product-box:hover .price-tag {
        transform: scale(1.1);
        filter: brightness(1.2);
    }
    
/* Shop buttons - Fixed for proper clickability */
.shop-buttons {
    display: flex;
    gap: 1rem;
    justify-content: center;
    margin-top: 1rem;
    z-index: 50;
    position: relative;
    /* Ensure this container doesn't block clicks */
    pointer-events: none;
}

/* Debug styles - add these temporarily to test */
.shop-btn {
    color: white !important;
    padding: 0.5rem 1rem;
    border-radius: 12px;
    text-decoration: none !important;
    font-size: 0.8rem;
    font-weight: 700;
    transition: all 0.3s ease;
    border: none;
    cursor: pointer !important;
    display: inline-block;
    text-align: center;
    vertical-align: middle;
    line-height: 1.2;
    position: relative;
    overflow: visible;
    min-width: 90px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    pointer-events: auto !important;
    user-select: none;
    z-index: 100 !important;
    transform-style: flat;
    /* Force dimensions */
    width: auto !important;
    height: auto !important;
    min-height: 32px;
}

/* Remove problematic pseudo-elements that block clicks */
.shop-btn::before,
.shop-btn::after {
    display: none !important; /* Completely disable pseudo-elements */
}

/* Ensure hover states work properly */
.shop-btn:hover,
.shop-btn:focus,
.shop-btn:active {
    transform: translateY(-2px) !important;
    text-decoration: none !important;
    color: white !important;
    outline: none;
    z-index: 101;
}

.shop-btn:visited {
    color: white !important;
    text-decoration: none !important;
}

/* Amazon button styles */
.shop-btn.amazon {
    background: linear-gradient(135deg, #ff9900, #e68900) !important;
}

.shop-btn.amazon:hover,
.shop-btn.amazon:focus {
    background: linear-gradient(135deg, #ffaa00, #ff9500) !important;
    box-shadow: 0 4px 15px rgba(255, 153, 0, 0.4);
}

.shop-btn.amazon:active {
    transform: translateY(0px) !important;
    background: linear-gradient(135deg, #e68900, #cc7700) !important;
}

/* Flipkart button styles */
.shop-btn.flipkart {
    background: linear-gradient(135deg, #2874f0, #1e5ce6) !important;
}

.shop-btn.flipkart:hover,
.shop-btn.flipkart:focus {
    background: linear-gradient(135deg, #3080ff, #2570e8) !important;
    box-shadow: 0 4px 15px rgba(40, 116, 240, 0.4);
}

.shop-btn.flipkart:active {
    transform: translateY(0px) !important;
    background: linear-gradient(135deg, #1e5ce6, #1a4db8) !important;
}

/* Icon styles - simplified */
.shop-btn i {
    font-size: 1.1rem;
    margin-right: 0.5rem;
    vertical-align: middle;
    pointer-events: none; /* Prevent icon from interfering with clicks */
}

/* Product box adjustments to prevent interference */
.product-box {
    background: rgba(0, 0, 0, 0.7) !important;
    border: 2px solid rgba(59, 130, 246, 0.3);
    border-radius: 20px;
    padding: 2rem;
    margin-bottom: 3rem;
    height: 450px;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    transition: all 0.4s ease;
    backdrop-filter: blur(15px);
    animation: productFloat 8s ease-in-out infinite;
    position: relative;
    box-shadow: 
        0 10px 30px rgba(0, 0, 0, 0.5),
        0 0 0 1px rgba(255, 255, 255, 0.05);
    width: 100% !important;
    max-width: 100% !important;
    box-sizing: border-box !important;
    overflow: visible; /* Changed from hidden to visible */
    z-index: 1; /* Lower z-index than buttons */
}

/* Remove problematic pseudo-element from product box */
.product-box::before {
    display: none !important;
}

/* Product info container - ensure it doesn't block clicks */
.product-info {
    text-align: center;
    margin-top: auto;
    position: relative;
    z-index: 2;
    /* Allow clicks to pass through to children */
    pointer-events: none;
}

/* Re-enable pointer events for interactive elements */
.product-info .price-tag {
    pointer-events: none;
}

.product-info .shop-buttons {
    pointer-events: none;
}

.product-info .shop-btn {
    pointer-events: auto !important;
}

/* Media query for mobile devices */
@media (max-width: 768px) {
    .shop-buttons {
        flex-direction: column;
        align-items: center;
        gap: 0.5rem;
        z-index: 50;
    }
    
    .shop-btn {
        width: 200px;
        padding: 0.75rem 1rem;
        display: block;
        text-align: center;
    }
}

/* Additional fixes for Streamlit markdown containers */
.stMarkdown {
    pointer-events: none !important;
}

.stMarkdown * {
    pointer-events: auto;
}

.stMarkdown .product-box {
    pointer-events: auto;
}

.stMarkdown .product-info {
    pointer-events: none;
}

.stMarkdown .shop-buttons {
    pointer-events: none;
}

.stMarkdown .shop-btn {
    pointer-events: auto !important;
}

/* Specific fix for nested anchor tags in Streamlit */
div[data-testid="stMarkdownContainer"] .shop-btn {
    pointer-events: auto !important;
    display: inline-block !important;
    position: relative !important;
    z-index: 999 !important;
}

/* Ensure Streamlit containers don't interfere */
.element-container {
    pointer-events: auto !important;
}

.element-container .product-box {
    pointer-events: auto;
}

.element-container .product-info {
    pointer-events: none;
}

.element-container .shop-btn {
    pointer-events: auto !important;
}

/* Ensure no global styles are interfering */
a.shop-btn {
    pointer-events: auto !important;
    display: inline-block !important;
    position: relative !important;
    z-index: 100 !important;
}

/* Remove any conflicting styles */
.enhanced-btn::after {
    display: none !important;
}

.neon-glow::before {
    pointer-events: none !important;
}
    
    /* Upload preview box */
    .upload-preview {
        background: rgba(0, 0, 0, 0.6);
        border: 1px solid rgba(255, 255, 255, 0.15);
        border-radius: 20px;
        padding: 2rem;
        text-align: center;
        backdrop-filter: blur(15px);
        height: 420px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        transition: all 0.4s ease;
        animation: previewFloat 10s ease-in-out infinite;
        margin-bottom: 2rem;
        width: 100% !important;
        max-width: 100% !important;
        box-sizing: border-box !important;
        box-shadow: 0 15px 35px rgba(0, 0, 0, 0.4);
    }
    
    @keyframes previewFloat {
        0%, 100% { transform: translateY(0px) rotateX(0deg); }
        50% { transform: translateY(-5px) rotateX(1deg); }
    }
    
    .upload-preview:hover {
        transform: translateY(-8px) scale(1.02) rotateY(2deg);
        box-shadow: 0 20px 40px rgba(59, 130, 246, 0.2);
        border-color: rgba(59, 130, 246, 0.3);
        background: rgba(0, 0, 0, 0.8);
    }
    
    .upload-preview h4 {
        color: #ffffff;
        margin-bottom: 1.5rem;
        font-weight: 700;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 0.75rem;
        font-size: 1.3rem;
        text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.5);
    }
    
    .upload-image-container {
        display: flex;
        justify-content: center;
        align-items: center;
        flex-grow: 1;
        width: 100%;
    }
    
    .upload-image-container img {
        max-width: 220px;
        max-height: 280px;
        object-fit: contain;
        border-radius: 15px;
        border: 1px solid rgba(255, 255, 255, 0.2);
        transition: all 0.4s ease;
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.3);
    }
    
    .upload-preview:hover .upload-image-container img {
        transform: scale(1.05) rotateY(3deg);
        box-shadow: 0 12px 30px rgba(59, 130, 246, 0.3);
        border-color: rgba(59, 130, 246, 0.3);
    }

    /* Category detection styling - static blue color */
    .category-badge {
        background: linear-gradient(135deg, #3b82f6, #2563eb, #1d4ed8);
        color: white;
        padding: 0.6rem 1.2rem;
        border-radius: 30px;
        font-size: 1rem;
        font-weight: 700;
        display: inline-flex;
        align-items: center;
        gap: 0.75rem;
        margin: 1rem 0;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        box-shadow: 0 6px 20px rgba(59, 130, 246, 0.3);
    }

    /* Radio button styling */
    .stRadio {
        background: rgba(0, 0, 0, 0.6);
        border: 1px solid rgba(255, 255, 255, 0.15);
        border-radius: 15px;
        padding: 1.2rem;
        margin: 1rem 0;
        backdrop-filter: blur(10px);
        transition: all 0.3s ease;
    }

    .stRadio:hover {
        border-color: rgba(59, 130, 246, 0.3);
        background: rgba(0, 0, 0, 0.8);
    }

    .stRadio label {
        color: #ffffff !important;
        font-weight: 600;
        text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.3);
    }

    /* Text input styling */
    .stTextInput input {
        background: rgba(0, 0, 0, 0.8) !important;
        border: 2px solid rgba(59, 130, 246, 0.3) !important;
        color: #ffffff !important;
        border-radius: 12px !important;
        padding: 0.9rem 1.2rem !important;
        transition: all 0.4s ease;
        backdrop-filter: blur(10px);
        font-weight: 500;
    }

    .stTextInput input:focus {
        border-color: rgba(59, 130, 246, 0.8) !important;
        box-shadow: 0 0 25px rgba(59, 130, 246, 0.3) !important;
        background: rgba(0, 0, 0, 0.9) !important;
    }
            
   /* Sample products styling - FULLY RESPONSIVE WITH BIGGER IMAGES */
.sample-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
    gap: 2.5rem 2rem;
    margin-top: 3rem;
    margin-bottom: 3rem;
    width: 100% !important;
    max-width: 100% !important;
    overflow: hidden !important;
    padding: 0 1rem;
}

/* Responsive grid adjustments */
@media (max-width: 1400px) {
    .sample-grid {
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 2rem 1.5rem;
    }
}

@media (max-width: 1200px) {
    .sample-grid {
        grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
        gap: 1.8rem 1.2rem;
    }
}

@media (max-width: 768px) {
    .sample-grid {
        grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
        gap: 1.5rem 1rem;
        padding: 0 0.5rem;
    }
}

@media (max-width: 480px) {
    .sample-grid {
        grid-template-columns: repeat(2, 1fr);
        gap: 1.2rem 0.8rem;
        padding: 0 0.2rem;
    }
}

/* Sample item styling with enhanced size and responsiveness */
.sample-item {
    background: #000000 !important;
    border: 2px solid rgba(59, 130, 246, 0.2);
    border-radius: 20px;
    padding: 1.8rem;
    text-align: center;
    transition: all 0.3s ease;
    animation: sampleFloat 7s ease-in-out infinite;
    height: auto;
    min-height: 420px;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
    backdrop-filter: blur(12px);
    margin-bottom: 2rem;
    width: 100% !important;
    max-width: 100% !important;
    box-sizing: border-box !important;
}

/* Responsive adjustments for sample items */
@media (max-width: 1200px) {
    .sample-item {
        min-height: 400px;
        padding: 1.6rem;
        border-radius: 18px;
    }
}

@media (max-width: 768px) {
    .sample-item {
        min-height: 380px;
        padding: 1.4rem;
        border-radius: 16px;
    }
}

@media (max-width: 480px) {
    .sample-item {
        min-height: 360px;
        padding: 1.2rem;
        border-radius: 14px;
    }
}

@keyframes sampleFloat {
    0%, 100% { transform: translateY(0px); }
    50% { transform: translateY(-3px); }
}

/* Subtle hover effects */
.sample-item:hover {
    transform: translateY(-4px) scale(1.01);
    box-shadow: 
        0 15px 35px rgba(59, 130, 246, 0.15),
        0 0 20px rgba(59, 130, 246, 0.08);
    background: #0a0a0a !important;
    border-color: rgba(59, 130, 246, 0.3);
    animation-play-state: paused;
}

/* Enhanced sample item image container - BIGGER IMAGES */
.sample-item-image {
    height: 260px;
    display: flex;
    align-items: center;
    justify-content: center;
    overflow: hidden;
    border-radius: 15px;
    background: #0a0a0a !important;
    margin-bottom: 1.2rem;
    transition: all 0.3s ease;
    border: 1px solid rgba(59, 130, 246, 0.1);
    position: relative;
}

/* Responsive image container sizes */
@media (max-width: 1200px) {
    .sample-item-image {
        height: 240px;
        border-radius: 14px;
    }
}

@media (max-width: 768px) {
    .sample-item-image {
        height: 220px;
        border-radius: 12px;
        margin-bottom: 1rem;
    }
}

@media (max-width: 480px) {
    .sample-item-image {
        height: 200px;
        border-radius: 10px;
        margin-bottom: 0.8rem;
        width: 100%;
        max-width: 100%;
    }
}

.sample-item:hover .sample-item-image {
    background: #111111 !important;
    transform: scale(1.01);
    border-color: rgba(59, 130, 246, 0.2);
    box-shadow: 0 4px 12px rgba(59, 130, 246, 0.1);
}

.sample-item img {
    max-width: 100%;
    max-height: 100%;
    object-fit: cover;
    border: none !important;
    border-radius: 12px;
    transition: all 0.3s ease;
    width: 100%;
    height: 100%;
}

@media (max-width: 768px) {
    .sample-item img {
        border-radius: 10px;
        object-fit: contain;
    }
}

@media (max-width: 480px) {
    .sample-item img {
        border-radius: 8px;
        object-fit: contain;
        max-height: 180px;
        width: auto;
        height: auto;
    }
}

.sample-item:hover img {
    transform: scale(1.02);
    filter: brightness(1.05);
}

/* Sample item text - responsive typography */
.sample-item-text {
    color: #ffffff;
    font-size: 1rem;
    font-weight: 600;
    margin-top: auto;
    line-height: 1.4;
    margin-bottom: 0.8rem;
    text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
}

@media (max-width: 768px) {
    .sample-item-text {
        font-size: 0.95rem;
        margin-bottom: 0.7rem;
    }
}

@media (max-width: 480px) {
    .sample-item-text {
        font-size: 0.9rem;
        margin-bottom: 0.6rem;
    }
}

/* SMALLER PRICE STYLING FOR SAMPLE PRODUCTS */
.sample-item .price-tag {
    color: #fbbf24;
    font-size: 1.1rem !important;
    font-weight: 700 !important;
    margin: 0.6rem 0 !important;
    transition: all 0.3s ease;
    text-shadow: 0 2px 4px rgba(251, 191, 36, 0.3);
    letter-spacing: 0.3px;
}

@media (max-width: 768px) {
    .sample-item .price-tag {
        font-size: 1rem !important;
        margin: 0.5rem 0 !important;
    }
}

@media (max-width: 480px) {
    .sample-item .price-tag {
        font-size: 0.95rem !important;
        margin: 0.4rem 0 !important;
    }
}

.sample-item:hover .price-tag {
    color: #f59e0b;
    transform: scale(1.03) !important;
    text-shadow: 0 3px 6px rgba(245, 158, 11, 0.4);
}

/* SMALLER SHOP BUTTONS - COMPACT SPACING */
.sample-item .shop-buttons,
.sample-product .shop-buttons {
    display: flex;
    gap: 2rem !important;
    justify-content: center;
    margin-top: 0.8rem !important;
    align-items: center;
}

@media (max-width: 768px) {
    .sample-item .shop-buttons,
    .sample-product .shop-buttons {
        gap: 1.5rem !important;
        margin-top: 0.6rem !important;
    }
}

@media (max-width: 480px) {
    .sample-item .shop-buttons,
    .sample-product .shop-buttons {
        gap: 1.2rem !important;
        margin-top: 0.5rem !important;
    }
}

/* Sample item icons - Smaller and more compact */
.sample-item .fab,
.sample-item .fas {
    font-size: 1.3rem !important;
    transition: all 0.3s ease;
    padding: 0.4rem;
    border-radius: 50%;
    background: rgba(255, 255, 255, 0.05);
    backdrop-filter: blur(5px);
}

@media (max-width: 768px) {
    .sample-item .fab,
    .sample-item .fas {
        font-size: 1.2rem !important;
        padding: 0.35rem;
    }
}

@media (max-width: 480px) {
    .sample-item .fab,
    .sample-item .fas {
        font-size: 1.1rem !important;
        padding: 0.3rem;
    }
}

.sample-item:hover .fab,
.sample-item:hover .fas {
    transform: scale(1.08) rotate(2deg);
    background: rgba(255, 255, 255, 0.08);
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
}

/* Enhanced Amazon icon for sample products */
.sample-item .fab.fa-amazon {
    color: #ff9900 !important;
    text-shadow: 0 2px 4px rgba(255, 153, 0, 0.3);
}

.sample-item:hover .fab.fa-amazon {
    color: #ffaa00 !important;
    text-shadow: 0 3px 6px rgba(255, 170, 0, 0.4);
    background: rgba(255, 153, 0, 0.08);
}

/* Enhanced Flipkart icon for sample products */
.sample-item .fas.fa-shopping-cart {
    color: #2874f0 !important;
    text-shadow: 0 2px 4px rgba(40, 116, 240, 0.3);
}

.sample-item:hover .fas.fa-shopping-cart {
    color: #3080ff !important;
    text-shadow: 0 3px 6px rgba(48, 128, 255, 0.4);
    background: rgba(40, 116, 240, 0.08);
}

/* Hide "Featured Products" text */
.sample-item .featured-text,
.sample-item .featured-label,
.sample-item::before {
    display: none !important;
}

/* Additional responsive improvements */
@media (max-width: 1400px) {
    .sample-item {
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.4);
    }
}

@media (max-width: 768px) {
    .sample-item {
        box-shadow: 0 6px 20px rgba(0, 0, 0, 0.4);
    }
    
    .sample-item:hover {
        transform: translateY(-3px) scale(1.01);
        box-shadow: 
            0 12px 30px rgba(59, 130, 246, 0.12),
            0 0 18px rgba(59, 130, 246, 0.06);
    }
}

@media (max-width: 480px) {
    .sample-item {
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
    }
    
    .sample-item:hover {
        transform: translateY(-2px) scale(1.005);
        box-shadow: 
            0 10px 25px rgba(59, 130, 246, 0.1),
            0 0 15px rgba(59, 130, 246, 0.05);
    }
}
    
    /* Responsive adjustments */
    @media (max-width: 768px) {
        .main-title {
            font-size: 2.8rem !important;
            flex-direction: column;
            text-align: center;
            gap: 1rem;
        }
        
        .title-icon {
            font-size: 2.5rem;
        }
        
        .header-section {
            text-align: center;
            margin-top: 4rem;
        }
        
        .top-bar {
            position: relative;
            top: 0;
            right: 0;
            margin-bottom: 2rem;
        }
        
        .upload-section-inline {
            flex-direction: column;
            gap: 1.5rem;
        }
        
        .main .block-container {
            padding-left: 0.5rem;
            padding-right: 0.5rem;
        }
        
        .product-box {
            height: 400px;
            margin-bottom: 2rem;
            padding: 1.5rem;
        }
        
        .product-image-container {
            height: 180px;
        }
        
        .shop-buttons {
            flex-direction: column;
            gap: 0.8rem !important;
        }
        
        .shop-btn {
            padding: 0.4rem 0.8rem !important;
            font-size: 0.75rem !important;
            min-width: 75px !important;
            gap: 0.3rem !important;
        }
        
        .shop-btn i {
            font-size: 0.9rem !important;
        }

        .upload-preview {
            height: 350px;
        }

        .upload-image-container img {
            max-width: 180px;
            max-height: 220px;
        }
    }

    /* Additional cool animations and effects */
    @keyframes shimmer {
        0% { transform: translateX(-100%); }
        100% { transform: translateX(100%); }
    }

    /* Particle effect overlay */
    .particles {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        pointer-events: none;
        z-index: 0;
    }

    .particle {
        position: absolute;
        width: 2px;
        height: 2px;
        background: rgba(255, 255, 255, 0.1);
        border-radius: 50%;
        animation: float 6s ease-in-out infinite;
    }

    @keyframes float {
        0%, 100% { transform: translateY(0px) translateX(0px); opacity: 0; }
        10% { opacity: 1; }
        90% { opacity: 1; }
        100% { transform: translateY(-100vh) translateX(50px); opacity: 0; }
    }

    /* Glassmorphism effect for key elements */
    .glass-effect {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        box-shadow: 
            0 8px 32px rgba(0, 0, 0, 0.3),
            inset 0 1px 0 rgba(255, 255, 255, 0.1);
    }

    /* Neon glow effects for interactive elements */
    .neon-glow {
        position: relative;
        overflow: hidden;
    }

    .neon-glow::before {
        content: '';
        position: absolute;
        top: -2px;
        left: -2px;
        right: -2px;
        bottom: -2px;
        background: linear-gradient(45deg, #3b82f6, #8b5cf6, #06b6d4, #10b981);
        border-radius: inherit;
        opacity: 0;
        transition: opacity 0.3s ease;
        z-index: -1;
        animation: neonRotate 4s linear infinite;
    }

    .neon-glow:hover::before {
        opacity: 0.7;
    }

    @keyframes neonRotate {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }

    /* Enhanced button hover states */
    .enhanced-btn {
        position: relative;
        overflow: hidden;
        transform-style: preserve-3d;
    }

    .enhanced-btn::after {
        content: '';
        position: absolute;
        top: 50%;
        left: 50%;
        width: 0;
        height: 0;
        background: radial-gradient(circle, rgba(255, 255, 255, 0.3) 0%, transparent 70%);
        transition: all 0.5s ease;
        border-radius: 50%;
        transform: translate(-50%, -50%);
    }

    .enhanced-btn:hover::after {
        width: 300px;
        height: 300px;
    }

    /* Staggered animation for product grid */
    .product-grid .product-box:nth-child(1) { animation-delay: 0s; }
    .product-grid .product-box:nth-child(2) { animation-delay: 0.2s; }
    .product-grid .product-box:nth-child(3) { animation-delay: 0.4s; }
    .product-grid .product-box:nth-child(4) { animation-delay: 0.6s; }

    /* Loading animation for image processing */
    .loading-spinner {
        border: 3px solid rgba(59, 130, 246, 0.2);
        border-top: 3px solid #3b82f6;
        border-radius: 50%;
        width: 40px;
        height: 40px;
        animation: spin 1s linear infinite;
        margin: 20px auto;
    }

    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }

    /* Success animation */
    .success-checkmark {
        width: 60px;
        height: 60px;
        border-radius: 50%;
        display: block;
        stroke-width: 3;
        stroke: #22c55e;
        stroke-miterlimit: 10;
        margin: 20px auto;
        box-shadow: inset 0px 0px 0px #22c55e;
        animation: fill 0.4s ease-in-out 0.4s forwards, scale 0.3s ease-in-out 0.9s both;
    }

    .success-checkmark__circle {
        stroke-dasharray: 166;
        stroke-dashoffset: 166;
        stroke-width: 3;
        stroke-miterlimit: 10;
        stroke: #22c55e;
        fill: none;
        animation: stroke 0.6s cubic-bezier(0.65, 0, 0.45, 1) forwards;
    }

    .success-checkmark__check {
        transform-origin: 50% 50%;
        stroke-dasharray: 48;
        stroke-dashoffset: 48;
        animation: stroke 0.3s cubic-bezier(0.65, 0, 0.45, 1) 0.8s forwards;
    }

    @keyframes stroke {
        100% { stroke-dashoffset: 0; }
    }

    @keyframes scale {
        0%, 100% { transform: none; }
        50% { transform: scale3d(1.1, 1.1, 1); }
    }

    @keyframes fill {
        100% { box-shadow: inset 0px 0px 0px 30px #22c55e; }
    }

    /* Tooltip styles */
    .tooltip {
        position: relative;
        display: inline-block;
    }

    .tooltip::after {
        content: attr(data-tooltip);
        position: absolute;
        bottom: 125%;
        left: 50%;
        transform: translateX(-50%);
        background: rgba(0, 0, 0, 0.9);
        color: white;
        padding: 8px 12px;
        border-radius: 8px;
        font-size: 0.8rem;
        white-space: nowrap;
        opacity: 0;
        visibility: hidden;
        transition: all 0.3s ease;
        z-index: 1000;
        border: 1px solid rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
    }

    .tooltip:hover::after {
        opacity: 1;
        visibility: visible;
    }

    /* Progress bar for uploads */
    .progress-bar {
        width: 100%;
        height: 6px;
        background: rgba(255, 255, 255, 0.1);
        border-radius: 3px;
        overflow: hidden;
        margin: 15px 0;
    }

    .progress-fill {
        height: 100%;
        background: linear-gradient(90deg, #3b82f6, #8b5cf6);
        border-radius: 3px;
        transition: width 0.3s ease;
        position: relative;
    }

    .progress-fill::after {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.3), transparent);
        animation: shimmer 2s infinite;
    }

    /* Custom scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
    }

    ::-webkit-scrollbar-track {
        background: rgba(0, 0, 0, 0.2);
        border-radius: 4px;
    }

    ::-webkit-scrollbar-thumb {
        background: linear-gradient(180deg, #3b82f6, #8b5cf6);
        border-radius: 4px;
        transition: all 0.3s ease;
    }

    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(180deg, #2563eb, #7c3aed);
    }

    /* Text selection styling */
    ::selection {
        background: rgba(59, 130, 246, 0.3);
        color: white;
    }

    ::-moz-selection {
        background: rgba(59, 130, 246, 0.3);
        color: white;
    }

    /* Focus states for accessibility */
    *:focus {
        outline: 2px solid rgba(59, 130, 246, 0.5);
        outline-offset: 2px;
    }

    /* Enhanced transitions for all interactive elements */
    button, a, input, .stFileUploader, .product-box, .shop-btn {
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }

    /* Dark theme enhancements */
    @media (prefers-color-scheme: dark) {
        .stApp {
            filter: brightness(1.1) contrast(1.05);
        }
    }

    /* Reduced motion for accessibility */
    @media (prefers-reduced-motion: reduce) {
        *, *::before, *::after {
            animation-duration: 0.01ms !important;
            animation-iteration-count: 1 !important;
            transition-duration: 0.01ms !important;
        }
    }

    /* High contrast mode support */
    @media (prefers-contrast: high) {
        .product-box {
            border-width: 3px;
        }
        
        .shop-btn {
            border: 2px solid white;
        }
        
        .stFileUploader {
            border-width: 3px;
        }
    }
    # Essential CSS for basic styling

/* Disable text selection and link behavior */
* {
   -webkit-user-select: none;
   -moz-user-select: none;
   -ms-user-select: none;
   user-select: none;
   text-decoration: none !important;
}

a, a:hover, a:visited, a:active {
   color: inherit !important;
   text-decoration: none !important;
   pointer-events: none !important;
}

.product-box:hover {
   transform: translateY(-5px);
   box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);
   transition: all 0.3s ease;
}

/* Hover effects for How it Works cards */
.work-step:hover {
   transform: translateY(-8px) scale(1.02);
   box-shadow: 0 15px 35px rgba(0, 0, 0, 0.4);
   transition: all 0.3s ease;
}

/* Hover effects for Technology cards */
.tech-item:hover {
   transform: translateY(-5px);
   transition: all 0.3s ease;
}

.tech-item:hover i {
   transform: scale(1.2);
   transition: all 0.3s ease;
}

/* Responsive design */
@media (max-width: 768px) {
   .main-title {
       font-size: 2.5rem !important;
   }
   
   .tagline {
       font-size: 1rem !important;
   }
}        
            
            </style>

""", unsafe_allow_html=True)

# Function to convert image to base64
def image_to_base64(img):
    """Convert PIL Image to base64 string for HTML display"""
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode()

# Function to convert URL image to base64
def url_to_base64(url):
    """Convert image from URL to base64 string"""
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        img = Image.open(response.raw).convert("RGB")
        return image_to_base64(img)
    except Exception as e:
        print(f"Error loading image from URL {url}: {e}")
        return ""

# Function to extract dominant colors from image
def get_dominant_colors(image, num_colors=3):
    """Extract dominant colors from PIL Image using simple method"""
    try:
        # Resize image for faster processing
        image = image.resize((50, 50))
        # Convert to numpy array
        img_array = np.array(image)
        # Get average color of the image
        avg_color = np.mean(img_array.reshape(-1, 3), axis=0)
        return avg_color
    except:
        return np.array([128, 128, 128])  # Default gray

# Function to calculate color similarity
def calculate_color_similarity(img1, img2):
    """Calculate similarity between two images based on dominant colors"""
    try:
        color1 = get_dominant_colors(img1)
        color2 = get_dominant_colors(img2)
        
        # Calculate Euclidean distance between average colors
        distance = np.sqrt(np.sum((color1 - color2) ** 2))
        
        # Convert distance to similarity (max distance for RGB is ~441)
        # Normalize to 0-1 range, then convert to percentage
        similarity = 1.0 - (distance / 441.0)
        
        # Ensure similarity is in reasonable range
        similarity = max(0.3, min(0.95, similarity))
        
        return similarity
    except Exception as e:
        # Fallback to decreasing similarity pattern
        return max(0.5, 0.9 - (shown_count * 0.05))

# Function to generate mock product info
def generate_product_info(category):
    """Generate mock price and shopping URLs"""
    category_prices = {
        "clothing": (800, 3000),
        "shoes": (1500, 8000),
        "electronics": (5000, 50000),
        "furniture": (2000, 25000),
        "accessories": (500, 5000)
    }
    
    price_range = category_prices.get(category.lower(), (500, 5000))
    price = random.randint(*price_range)
    
    # Generic search URLs
    amazon_url = f"https://amazon.in/s?k={category.replace(' ', '+')}"
    flipkart_url = f"https://flipkart.com/search?q={category.replace(' ', '%20')}"
    
    return price, amazon_url, flipkart_url

# Function to generate product info from URL (for sample products)
def generate_product_info_from_url(url, category_to_urls):
    """Generate mock price and shopping URLs for sample products"""
    # Find the actual category for this URL
    actual_category = None
    for category, urls in category_to_urls.items():
        if url in urls:
            actual_category = category
            break
    
    # If category not found, use a random one as fallback
    if actual_category is None:
        categories = ["clothing", "shoes", "electronics", "furniture", "accessories"]
        actual_category = random.choice(categories)
    
    return generate_product_info(actual_category)

# Load model
@st.cache_resource
def load_model():
    model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
    processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
    return model, processor

model, processor = load_model()

# Load category data
@st.cache_data
def load_category_data():
    try:
        with open("data/valid_image_urls.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        st.error("❌ Please ensure 'data/valid_image_urls.json' exists in your project directory.")
        return {}

category_to_urls = load_category_data()

# Create main layout
main_col1, main_col2 = st.columns([2, 1], gap="large")

# Left column - Header and About
with main_col1:
    st.markdown("""
    <div class="header-section">
        <div class="main-title">
            <i class="fa-solid fa-cart-arrow-down">‌</i>
            Pic2Pick
        </div>
        <div class="tagline">
            See It. Snap It. Get It.
        </div>
        <div class="about-section">
            Pic2Pick is a smart visual search engine that helps you instantly find similar products using just an image. Whether it's fashion, furniture, or gadgets — simply upload a picture or use a URL, and discover visually matching items in seconds. Fast, intuitive, and AI-powered — with direct shopping links to buy what you love, effortlessly.
        </div>
    </div>
    """, unsafe_allow_html=True)

# Right column - Upload section
with main_col2:
    st.markdown('<div class="upload-section">', unsafe_allow_html=True)
    
    # Input method selection
    option = st.radio(
        "Choose input method:",
        ["Upload an Image", "Paste Image URL"],
        help="Select how you want to provide your product image"
    )
    
    image = None
    
    if option == "Upload an Image":
        uploaded_file = st.file_uploader(
            "", 
            type=["jpg", "jpeg", "png"],
            help="Upload a clear image of the product you're looking for",
            label_visibility="collapsed"
        )
        
        st.markdown("""
        <div style="text-align: center; margin-bottom: 1rem; color: #ffffff;">
            <i class="fas fa-cloud-upload-alt" style="font-size: 1.5rem; margin-right: 0.5rem;"></i>
            <strong>Upload Your Product Image</strong>
        </div>
        """, unsafe_allow_html=True)
        
        if uploaded_file:
            image = Image.open(uploaded_file).convert("RGB")
            
    elif option == "Paste Image URL":
        url = st.text_input("Paste image URL:", placeholder="https://example.com/image.jpg")
        if url:
            try:
                response = requests.get(url, stream=True)
                response.raise_for_status()
                image = Image.open(response.raw).convert("RGB")
            except Exception as e:
                st.error(f"❌ Failed to load image from URL: {e}")
    
    st.markdown('</div>', unsafe_allow_html=True)

# Process image if available
if image and category_to_urls:
    # Create responsive layout for results
    result_col1, result_col2 = st.columns([3, 1], gap="large")
    
    try:
        # Generate query embedding
        inputs = processor(images=image, return_tensors="pt")
        query_feature = model.get_image_features(**inputs).detach().numpy()

        # Auto-detect category by checking closest match across all categories
        best_category = None
        best_distance = float("inf")
        best_index = None
        best_urls = []

        for category, urls in category_to_urls.items():
            feature_file = f"data/features_{category}.npy"
            if not os.path.exists(feature_file):
                continue

            try:
                features = np.load(feature_file)
                index = faiss.IndexFlatL2(features.shape[1])
                index.add(features)

                D, I = index.search(query_feature, k=1)
                if D[0][0] < best_distance:
                    best_distance = D[0][0]
                    best_category = category
                    best_index = index
                    best_urls = urls
            except Exception as e:
                print(f"Error loading category {category}: {e}")

        # Right column - Upload preview
        with result_col2:
            img_base64 = image_to_base64(image)
            
            st.markdown(f"""
            <div class="upload-preview">
                <h4><i class="fas fa-camera icon"></i> Your Upload</h4>
                <div class="upload-image-container">
                    <img src="data:image/png;base64,{img_base64}" alt="Uploaded Image">
                </div>
            </div>
            """, unsafe_allow_html=True)

        # Left column - Results
        with result_col1:
            if best_category is None:
                st.error("❌ Could not match your image to any category. Please try a different image.")
            else:
                # Show detected category
                st.markdown(f"""
                <div class="category-badge">
                    <i class="fas fa-check-circle"></i>
                    Detected Category: {best_category.title()}
                </div>
                """, unsafe_allow_html=True)

                # Get top matches and show unique images
                features = np.load(f"data/features_{best_category}.npy")
                index = faiss.IndexFlatL2(features.shape[1])
                index.add(features)
                D, I = index.search(query_feature, k=20)

                st.markdown("""
                <div style="margin: 2rem 0;">
                    <h3 style="color: #ffffff; font-weight: 600; margin-bottom: 1.5rem;">
                        <i class="fas fa-star icon" style="color: #fbbf24; margin-right: 0.5rem;"></i>
                        Similar Products Found
                    </h3>
                </div>
                """, unsafe_allow_html=True)

                # Display results in grid
                shown_urls = set()
                shown_count = 0
                max_results = 6

                # Calculate number of rows needed
                cols_per_row = 2
                rows = (max_results + cols_per_row - 1) // cols_per_row

                for row in range(rows):
                    if shown_count >= max_results:
                        break
                        
                    cols = st.columns(cols_per_row, gap="medium")
                    
                    for col_idx in range(cols_per_row):
                        if shown_count >= max_results:
                            break
                            
                        # Find next unique URL
                        found_url = None
                        distance_for_similarity = None
                        for i, idx in enumerate(I[0]):
                            if idx >= len(best_urls):
                                continue
                            url = best_urls[idx]
                            if url not in shown_urls:
                                shown_urls.add(url)
                                found_url = url
                                distance_for_similarity = D[0][i]
                                break
                        
                        if found_url:
                            with cols[col_idx]:
                                try:
                                    # Convert URL image to base64
                                    response = requests.get(found_url, stream=True)
                                    response.raise_for_status()
                                    url_image = Image.open(response.raw).convert("RGB")
                                    url_img_base64 = image_to_base64(url_image)
                                    
                                    # Generate product info
                                    price, amazon_url, flipkart_url = generate_product_info(best_category)
                                    
                                    # Calculate similarity based on color analysis
                                    try:
                                        similarity = calculate_color_similarity(image, url_image)
                                    except:
                                        # Simple fallback based on position
                                        similarity = max(0.5, 0.9 - (shown_count * 0.05))
                                    
                                    # Create product box
                                    st.markdown(f"""
                                    <div class="product-box">
                                        <div class="product-header">
                                            <div class="product-title">
                                                <i class="fas fa-gift icon"></i> Similar Product
                                            </div>
                                            <div class="similarity-badge-header">{similarity:.1%}</div>
                                        </div>
                                        <div class="product-image-container">
                                            <img src="data:image/png;base64,{url_img_base64}" alt="Similar Product">
                                        </div>
                                        <div class="product-info">
                                            <div class="price-tag">₹{price:,}</div>
                                            <div class="shop-buttons">
                                                <a href="{amazon_url}" target="_blank" class="shop-btn amazon">
                                                    <i class="fab fa-amazon"></i> Amazon
                                                </a>
                                                <a href="{flipkart_url}" target="_blank" class="shop-btn flipkart">
                                                    <i class="fas fa-shopping-cart"></i> Flipkart
                                                </a>
                                            </div>
                                        </div>
                                    </div>
                                    """, unsafe_allow_html=True)
                                    
                                    shown_count += 1
                                    
                                except Exception as e:
                                    print(f"Error loading image from URL {found_url}: {e}")
                                    continue

    except Exception as e:
        st.error(f"❌ An error occurred while processing your image: {e}")

# NEW RECOMMENDATION SECTION - Show sample products when no image is uploaded
else:
    # Show sample products in enhanced grid
    if category_to_urls:
        # Collect image paths from all categories
        image_paths = []
        for category, urls in category_to_urls.items():
            image_paths.extend(urls)
        
        if len(image_paths) > 0:
            st.markdown("""
            <div style="text-align: center; margin: 3rem 0;">
                <h3 style="color: #ffffff; font-weight: 600; margin-bottom: 1.5rem;">
                    <i class="fas fa-star icon" style="color: #fbbf24; margin-right: 0.5rem;"></i>
                    Explore Our Featured Products
                </h3>
                <p style="color: #d1d5db; font-size: 1rem; margin-bottom: 2rem;">
                    Discover trending items across various categories. Upload an image to find similar products!
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            # Display sample products in a grid
            sample_size = min(8, len(image_paths))  # Show up to 8 sample products
            sample_indices = random.sample(range(len(image_paths)), sample_size)
            
            # Create responsive grid layout
            num_cols = 4
            rows = (sample_size + num_cols - 1) // num_cols
            
            for row in range(rows):
                cols = st.columns(num_cols, gap="medium")
                for col_idx in range(num_cols):
                    sample_idx = row * num_cols + col_idx
                    if sample_idx < sample_size:
                        actual_idx = sample_indices[sample_idx]
                        with cols[col_idx]:
                            img_path = image_paths[actual_idx]
                            price, amazon_url, flipkart_url = generate_product_info_from_url(img_path, category_to_urls)
                            
                            # Get base64 encoded image
                            img_base64 = url_to_base64(img_path)
                            
                            if img_base64:  # Only show if image loads successfully
                                # Create sample product card
                                st.markdown(f"""
                                <div class="sample-item">
                                    <div class="sample-item-image">
                                        <img src="data:image/jpeg;base64,{img_base64}" 
                                             alt="Sample Product">
                                    </div>
                                    <div class="sample-item-text">Featured Product</div>
                                    <div class="price-tag">₹{price:,}</div>
                                    <div class="shop-buttons">
                                        <a href="{amazon_url}" target="_blank" style="color: #ff9900; text-decoration: none;">
                                            <i class="fab fa-amazon"></i>
                                        </a>
                                        <a href="{flipkart_url}" target="_blank" style="color: #2874f0; text-decoration: none;">
                                            <i class="fas fa-shopping-cart"></i>
                                        </a>
                                    </div>
                                </div>
                                """, unsafe_allow_html=True)

# How it works section - Black glass background
st.markdown("""
<div style="margin: 4cm 0 3rem 0;">
   <h3 style="text-align: center; color: #ffffff; margin-bottom: 2rem; font-weight: 600;">
       <i class="fas fa-cogs icon" style="color: #3b82f6; margin-right: 0.5rem;"></i>
       How Pic2Pick Works
   </h3>
   <div style="background: rgba(0, 0, 0, 0.7); border: 1px solid rgba(255, 255, 255, 0.1); 
               border-radius: 15px; padding: 2rem; backdrop-filter: blur(10px);">
       <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 1.5rem;">
           <div class="work-step" style="background: rgba(139, 69, 19, 0.2); border: 1px solid rgba(139, 69, 19, 0.3); 
                       border-radius: 15px; padding: 1.5rem; text-align: center;">
               <div style="color: #cd853f; font-size: 2.5rem; margin-bottom: 1rem;">
                   <i class="fas fa-upload"></i>
               </div>
               <h4 style="color: #ffffff; margin-bottom: 0.5rem;">1. Upload Image</h4>
               <p style="color: #d1d5db; font-size: 0.9rem; margin: 0;">
                   Simply upload a clear photo of any product you want to find
               </p>
           </div>
           <div class="work-step" style="background: rgba(168, 85, 247, 0.2); border: 1px solid rgba(168, 85, 247, 0.3); 
                       border-radius: 15px; padding: 1.5rem; text-align: center;">
               <div style="color: #a855f7; font-size: 2.5rem; margin-bottom: 1rem;">
                   <i class="fas fa-brain"></i>
               </div>
               <h4 style="color: #ffffff; margin-bottom: 0.5rem;">2. AI Analysis</h4>
               <p style="color: #d1d5db; font-size: 0.9rem; margin: 0;">
                   Our AI extracts visual features and compares with our database
               </p>
           </div>
           <div class="work-step" style="background: rgba(34, 197, 94, 0.2); border: 1px solid rgba(34, 197, 94, 0.3); 
                       border-radius: 15px; padding: 1.5rem; text-align: center;">
               <div style="color: #22c55e; font-size: 2.5rem; margin-bottom: 1rem;">
                   <i class="fas fa-search"></i>
               </div>
               <h4 style="color: #ffffff; margin-bottom: 0.5rem;">3. Find Matches</h4>
               <p style="color: #d1d5db; font-size: 0.9rem; margin: 0;">
                   FAISS indexing finds visually similar products with high accuracy
               </p>
           </div>
           <div class="work-step" style="background: rgba(249, 115, 22, 0.2); border: 1px solid rgba(249, 115, 22, 0.3); 
                       border-radius: 15px; padding: 1.5rem; text-align: center;">
               <div style="color: #f97316; font-size: 2.5rem; margin-bottom: 1rem;">
                   <i class="fas fa-shopping-cart"></i>
               </div>
               <h4 style="color: #ffffff; margin-bottom: 0.5rem;">4. Shop Now</h4>
               <p style="color: #d1d5db; font-size: 0.9rem; margin: 0;">
                   Get direct links to Amazon & Flipkart with pricing information
               </p>
           </div>
       </div>
   </div>
</div>
""", unsafe_allow_html=True)

# Technology highlights - Solid black background
st.markdown("""
<div style="background: #000000; border: 1px solid rgba(255, 255, 255, 0.1); 
           border-radius: 15px; padding: 2rem; margin: 2rem 0;">
   <h4 style="color: #ffffff; text-align: center; margin-bottom: 1.5rem; font-weight: 600;">
       <i class="fas fa-microchip icon" style="color: #6366f1; margin-right: 0.5rem;"></i>
       Powered by Advanced Technology
   </h4>
   <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem; text-align: center;">
       <div class="tech-item">
           <i class="fas fa-robot" style="color: #3b82f6; font-size: 1.5rem; margin-bottom: 0.5rem;"></i>
           <div style="color: #ffffff; font-weight: 600;">Deep Learning</div>
           <div style="color: #9ca3af; font-size: 0.8rem;">Neural networks for feature extraction</div>
       </div>
       <div class="tech-item">
           <i class="fas fa-database" style="color: #10b981; font-size: 1.5rem; margin-bottom: 0.5rem;"></i>
           <div style="color: #ffffff; font-weight: 600;">FAISS Indexing</div>
           <div style="color: #9ca3af; font-size: 0.8rem;">Lightning-fast similarity search</div>
       </div>
       <div class="tech-item">
           <i class="fas fa-eye" style="color: #f59e0b; font-size: 1.5rem; margin-bottom: 0.5rem;"></i>
           <div style="color: #ffffff; font-weight: 600;">Computer Vision</div>
           <div style="color: #9ca3af; font-size: 0.8rem;">Advanced image understanding</div>
       </div>
       <div class="tech-item">
           <i class="fas fa-cloud" style="color: #8b5cf6; font-size: 1.5rem; margin-bottom: 0.5rem;"></i>
           <div style="color: #ffffff; font-weight: 600;">Cloud Powered</div>
           <div style="color: #9ca3af; font-size: 0.8rem;">Scalable and reliable infrastructure</div>
       </div>
   </div>
</div>
""", unsafe_allow_html=True)


          

# Footer
st.markdown("""
    <div style="margin-top: 4rem; padding: 2rem; text-align: center; color: #60a5fa; border-top: 1px solid #ffffff;">
    <p style="font-size: 0.9rem; margin: 0;">
        Made by Shivam with <i class="fas fa-heart" style="color: #ef4444;"></i>
    </p>
</div>
""", unsafe_allow_html=True)