import os
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

import streamlit as st
from components.navbar import render_navbar
from components.footer import render_footer
from PIL import Image
import os
import numpy as np
import torch
import clip
import faiss
import random
import base64
from io import BytesIO

render_navbar()

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
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    @import url('https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css');
    
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

/* Main app background with animated grid */
.stApp {
    background: #0a0a0a;
    font-family: 'Inter', sans-serif;
    position: relative;
    overflow-x: hidden !important;
    max-width: 100vw !important;
    width: 100vw !important;
}

/* Animated grid background */
.stApp::before {
    content: '';
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background-image: 
        linear-gradient(rgba(255, 255, 255, 0.12) 1px, transparent 1px),
        linear-gradient(90deg, rgba(255, 255, 255, 0.12) 1px, transparent 1px);
    background-size: 50px 50px;
    animation: gridMove 20s linear infinite;
    z-index: 0;
    pointer-events: none;
}

@keyframes gridMove {
    0% { transform: translate(0, 0); }
    100% { transform: translate(50px, 50px); }
}

/* Subtle overlay for professional look */
.stApp::after {
    content: '';
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: 
        radial-gradient(circle at 20% 30%, rgba(59, 130, 246, 0.15) 0%, transparent 50%),
        radial-gradient(circle at 80% 70%, rgba(168, 85, 247, 0.12) 0%, transparent 50%);
    z-index: 0;
    pointer-events: none;
    animation: subtleGlow 15s ease-in-out infinite;
}

@keyframes subtleGlow {
    0%, 100% { opacity: 0.8; }
    50% { opacity: 1; }
}

/* Ensure Streamlit content appears above background */
.stApp > div {
    position: relative;
    z-index: 1;
}
    
    /* Main container adjustments */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        padding-left: 1rem; /* Reduced from 1.5rem to increase width */
        padding-right: 1rem; /* Reduced from 1.5rem to increase width */
        background: rgba(15, 15, 15, 0.85);
        backdrop-filter: blur(10px);
        border-radius: 20px;
        margin-top: 1rem;
        border: 1px solid rgba(255, 255, 255, 0.08);
        animation: containerFloat 10s ease-in-out infinite;
        max-width: 100% !important;
        overflow-x: hidden !important;
    }
    
    @keyframes containerFloat {
        0%, 100% { transform: translateY(0px); }
        50% { transform: translateY(-3px); }
    }
    
    /* Header section styling */
    .header-section {
        text-align: left;
        margin-bottom: 2rem;
        animation: slideInLeft 1s ease-out;
    }
    
    @keyframes slideInLeft {
        from { opacity: 0; transform: translateX(-50px); }
        to { opacity: 1; transform: translateX(0); }
    }
    
    /* Title styling */
    .main-title {
        color: #ffffff !important;
        font-weight: 700 !important;
        font-size: 3.5rem !important;
        margin-bottom: 0.5rem !important;
        display: flex;
        align-items: center;
        gap: 1rem;
    }
    
    .title-icon {
        font-size: 3rem;
        color: #3b82f6; /* Professional blue */
        animation: iconBounce 2s ease-in-out infinite;
    }
    
    @keyframes iconBounce {
        0%, 100% { transform: translateY(0px); }
        50% { transform: translateY(-8px); }
    }
    
    /* Tagline styling */
    .tagline {
        color: #60a5fa !important; /* Light blue */
        font-size: 1.3rem !important;
        font-weight: 600 !important;
        margin-bottom: 1rem !important;
        font-style: italic;
        animation: fadeInUp 1.5s ease-out 0.5s both;
    }
    
    @keyframes fadeInUp {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    /* About section styling */
    .about-section {
        color: #d1d5db !important;
        font-size: 1.1rem !important;
        line-height: 1.6 !important;
        margin-bottom: 2rem !important;
        animation: fadeInUp 1.5s ease-out 1s both;
    }
    
    /* Upload section styling */
    .upload-section {
        animation: slideInRight 1s ease-out;
        margin-top: 3rem;
    }
    
    @keyframes slideInRight {
        from { opacity: 0; transform: translateX(50px); }
        to { opacity: 1; transform: translateX(0); }
    }
    
    /* Enhanced file uploader with solid black background - INCREASED WIDTH */
    .stFileUploader {
        background: #000000 !important;
        border: 2px dashed rgba(59, 130, 246, 0.4);
        border-radius: 15px;
        padding: 2rem;
        text-align: center;
        margin: 2.5rem -1rem; /* Negative margin to extend beyond container padding */
        transition: all 0.3s ease;
        animation: uploadPulse 4s ease-in-out infinite;
        width: calc(100% + 2rem) !important; /* Compensate for negative margin */
        max-width: calc(100% + 2rem) !important;
        box-sizing: border-box !important;
    }
    
    @keyframes uploadPulse {
        0%, 100% { box-shadow: 0 0 20px rgba(59, 130, 246, 0.15); }
        50% { box-shadow: 0 0 30px rgba(59, 130, 246, 0.25); }
    }
    
    .stFileUploader:hover {
        border-color: rgba(59, 130, 246, 0.7);
        background: #111111 !important;
        transform: translateY(-3px) scale(1.01);
        box-shadow: 0 12px 35px rgba(59, 130, 246, 0.2);
        animation-play-state: paused;
    }
    
    .stFileUploader label {
        color: #ffffff !important;
        font-size: 1rem !important;
        font-weight: 500 !important;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 0.5rem;
    }
    
    /* Smaller Browse Files text */
    .stFileUploader label div {
        font-size: 0.9rem !important;
    }
    
    /* Enhanced spacing for columns - Better gaps between product boxes */
    .stColumns {
        gap: 2rem !important;
        margin: 3rem 0 !important;
        max-width: 100% !important;
        overflow-x: hidden !important;
    }
    
    .stColumns > div {
        padding: 0 1rem !important;
        max-width: calc(50% - 1rem) !important;
        flex: 1 !important;
        box-sizing: border-box !important;
    }
    
    /* Product boxes with solid black background and REDUCED HOVER GLOW */
    .product-box {
        background: #000000 !important;
        border: 2px solid rgba(59, 130, 246, 0.2);
        border-radius: 18px;
        padding: 2rem;
        margin-bottom: 3rem;
        height: 420px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        transition: all 0.3s ease;
        backdrop-filter: blur(10px);
        animation: productFloat 6s ease-in-out infinite;
        position: relative;
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.4);
        width: 100% !important;
        max-width: 100% !important;
        box-sizing: border-box !important;
    }
    
    @keyframes productFloat {
        0%, 100% { transform: translateY(0px); }
        50% { transform: translateY(-2px); }
    }
    
    .product-box:hover {
        transform: translateY(-10px) scale(1.03);
        box-shadow: 
            0 15px 35px rgba(59, 130, 246, 0.15), /* Reduced from 0.25 */
            0 0 20px rgba(59, 130, 246, 0.08); /* Reduced from 0.1 */
        border-color: rgba(59, 130, 246, 0.5);
        background: #111111 !important;
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
        font-size: 0.9rem;
    }
    
    .product-title {
        display: flex;
        align-items: center;
        gap: 0.3rem;
    }
    
    .similarity-badge-header {
        background: linear-gradient(135deg, #3b82f6, #1d4ed8);
        color: white;
        padding: 0.2rem 0.6rem;
        border-radius: 15px;
        font-size: 0.75rem;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .product-box:hover .similarity-badge-header {
        transform: scale(1.05);
        box-shadow: 0 2px 8px rgba(59, 130, 246, 0.3);
    }
    
    .product-image-container {
        height: 220px;
        display: flex;
        align-items: center;
        justify-content: center;
        overflow: hidden;
        border-radius: 12px;
        background: #0a0a0a !important;
        margin-bottom: 1.5rem;
        transition: all 0.3s ease;
        border: 1px solid rgba(59, 130, 246, 0.1);
    }
    
    .product-box:hover .product-image-container {
        background: #1a1a1a !important;
        transform: scale(1.02);
        border-color: rgba(59, 130, 246, 0.2);
    }
    
    .product-image-container img {
        max-width: 100%;
        max-height: 100%;
        object-fit: contain;
        border-radius: 8px;
        transition: all 0.3s ease;
    }
    
    .product-info {
        text-align: center;
        margin-top: auto;
    }
    
    .price-tag {
        color: #fbbf24;
        font-size: 1.1rem;
        font-weight: 600;
        margin: 0.5rem 0;
        transition: all 0.3s ease;
    }
    
    .product-box:hover .price-tag {
        color: #f59e0b;
        transform: scale(1.05);
    }
    
    /* SMALLER SHOP BUTTONS FOR RECOMMENDED PRODUCTS */
    .shop-buttons {
        display: flex;
        gap: 1rem; /* Reduced gap for smaller buttons */
        justify-content: center;
        margin-top: 1rem;
    }
    
    /* Enhanced shop buttons - SMALLER SIZE FOR RECOMMENDED PRODUCTS */
    .shop-btn {
        color: white !important;
        padding: 0.4rem 0.8rem !important; /* REDUCED from 0.6rem 1.2rem */
        border-radius: 8px !important; /* REDUCED from 12px */
        text-decoration: none !important;
        font-size: 0.75rem !important; /* REDUCED from 0.85rem */
        font-weight: 600;
        transition: all 0.3s ease;
        border: none;
        cursor: pointer;
        display: flex;
        align-items: center;
        gap: 0.3rem !important; /* REDUCED from 0.4rem */
        position: relative;
        overflow: hidden;
        min-width: 80px !important; /* REDUCED from 100px */
        justify-content: center;
    }
    
    .shop-btn::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.15), transparent);
        transition: left 0.5s;
    }
    
    .shop-btn:hover::before {
        left: 100%;
    }
    
    .shop-btn:hover {
        transform: translateY(-2px) scale(1.05);
        text-decoration: none !important;
        color: white !important;
    }
    
    .shop-btn.amazon {
        background: linear-gradient(135deg, #ff9900, #e68900);
        box-shadow: 0 4px 15px rgba(255, 153, 0, 0.2);
    }
    
    .shop-btn.amazon:hover {
        box-shadow: 0 6px 20px rgba(255, 153, 0, 0.35);
        background: linear-gradient(135deg, #ffaa00, #ff9500);
    }
    
    .shop-btn.flipkart {
        background: linear-gradient(135deg, #2874f0, #1e5ce6);
        box-shadow: 0 4px 15px rgba(40, 116, 240, 0.2);
    }
    
    .shop-btn.flipkart:hover {
        box-shadow: 0 6px 20px rgba(40, 116, 240, 0.35);
        background: linear-gradient(135deg, #3080ff, #2570e8);
    }
    
    /* Icon styling for buttons - SMALLER ICONS FOR RECOMMENDED PRODUCTS */
    .shop-btn i {
        font-size: 1rem !important; /* REDUCED from 1.2rem */
        transition: transform 0.3s ease;
    }
    
    .shop-btn:hover i {
        transform: scale(1.1) rotate(3deg);
    }
    
    /* Upload preview box with better spacing */
    .upload-preview {
        background: rgba(255, 255, 255, 0.04);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 15px;
        padding: 2rem;
        text-align: center;
        backdrop-filter: blur(10px);
        height: 400px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        transition: all 0.3s ease;
        animation: previewFloat 8s ease-in-out infinite;
        margin-bottom: 2rem;
        width: 100% !important;
        max-width: 100% !important;
        box-sizing: border-box !important;
    }
    
    @keyframes previewFloat {
        0%, 100% { transform: translateY(0px); }
        50% { transform: translateY(-3px); }
    }
    
    .upload-preview:hover {
        transform: translateY(-5px) scale(1.01);
        box-shadow: 0 12px 30px rgba(59, 130, 246, 0.15);
        border-color: rgba(59, 130, 246, 0.2);
    }
    
    .upload-preview h4 {
        color: #ffffff;
        margin-bottom: 1.5rem;
        font-weight: 600;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 0.5rem;
    }
    
    .upload-image-container {
        display: flex;
        justify-content: center;
        align-items: center;
        flex-grow: 1;
        width: 100%;
    }
    
    .upload-image-container img {
        max-width: 200px;
        max-height: 250px;
        object-fit: contain;
        border-radius: 10px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        transition: all 0.3s ease;
    }
    
    .upload-preview:hover .upload-image-container img {
        transform: scale(1.03);
        box-shadow: 0 8px 25px rgba(59, 130, 246, 0.2);
    }
    
    /* Sample products styling - CONTAINED WITHIN VIEWPORT */
    .sample-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
        gap: 2rem 2rem;
        margin-top: 3rem;
        margin-bottom: 3rem;
        width: 100% !important;
        max-width: 100% !important;
        overflow: hidden !important;
    }

    /* Sample item styling with enhanced price and button spacing */
    .sample-item {
        background: #000000 !important;
        border: 2px solid rgba(59, 130, 246, 0.2);
        border-radius: 18px;
        padding: 1.5rem;
        text-align: center;
        transition: all 0.3s ease;
        animation: sampleFloat 7s ease-in-out infinite;
        height: 300px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.4);
        backdrop-filter: blur(10px);
        margin-bottom: 2rem;
        width: 100% !important;
        max-width: 100% !important;
        box-sizing: border-box !important;
    }
    
    @keyframes sampleFloat {
        0%, 100% { transform: translateY(0px); }
        50% { transform: translateY(-2px); }
    }
    
    .sample-item:hover {
        transform: translateY(-10px) scale(1.03);
        box-shadow: 
            0 20px 50px rgba(59, 130, 246, 0.25),
            0 0 30px rgba(59, 130, 246, 0.1);
        background: #111111 !important;
        border-color: rgba(59, 130, 246, 0.5);
        animation-play-state: paused;
    }
    
    /* Sample item image container */
    .sample-item-image {
        height: 160px;
        display: flex;
        align-items: center;
        justify-content: center;
        overflow: hidden;
        border-radius: 12px;
        background: #0a0a0a !important;
        margin-bottom: 1rem;
        transition: all 0.3s ease;
        border: 1px solid rgba(59, 130, 246, 0.1);
    }
    
    .sample-item:hover .sample-item-image {
        background: #1a1a1a !important;
        transform: scale(1.02);
        border-color: rgba(59, 130, 246, 0.2);
    }
    
    .sample-item img {
        max-width: 100%;
        max-height: 100%;
        object-fit: contain;
        border: none !important;
        border-radius: 8px;
        transition: all 0.3s ease;
    }
    
    /* Sample item text */
    .sample-item-text {
        color: #ffffff;
        font-size: 0.9rem;
        font-weight: 500;
        margin-top: auto;
        line-height: 1.3;
    }

    /* ENHANCED PRICE STYLING FOR SAMPLE PRODUCTS */
    .sample-item .price-tag {
        color: #fbbf24;
        font-size: 1.3rem !important;
        font-weight: 700 !important;
        margin: 0.8rem 0 !important;
        transition: all 0.3s ease;
        text-shadow: 0 2px 4px rgba(251, 191, 36, 0.3);
    }
    
    .sample-item:hover .price-tag {
        color: #f59e0b;
        transform: scale(1.08) !important;
        text-shadow: 0 3px 6px rgba(245, 158, 11, 0.4);
    }

    /* SAMPLE ITEM SHOP BUTTONS - KEEP ORIGINAL SIZE FOR SAMPLE PRODUCTS */
    .sample-item .shop-buttons,
    .sample-product .shop-buttons {
        display: flex;
        gap: 2.5rem !important;
        justify-content: center;
        margin-top: 1rem !important;
    }

    /* Sample item icons - Enhanced for better visibility */
    .sample-item .fab,
    .sample-item .fas {
        font-size: 1.5rem !important;
        transition: transform 0.3s ease;
        padding: 0.3rem;
    }

    .sample-item:hover .fab,
    .sample-item:hover .fas {
        transform: scale(1.15) rotate(3deg);
    }

    /* Enhanced Amazon icon for sample products */
    .sample-item .fab.fa-amazon {
        color: #ff9900 !important;
        text-shadow: 0 2px 4px rgba(255, 153, 0, 0.3);
    }

    .sample-item:hover .fab.fa-amazon {
        color: #ffaa00 !important;
        text-shadow: 0 3px 6px rgba(255, 170, 0, 0.4);
    }

    /* Enhanced Flipkart icon for sample products */
    .sample-item .fas.fa-shopping-cart {
        color: #2874f0 !important;
        text-shadow: 0 2px 4px rgba(40, 116, 240, 0.3);
    }

    .sample-item:hover .fas.fa-shopping-cart {
        color: #3080ff !important;
        text-shadow: 0 3px 6px rgba(48, 128, 255, 0.4);
    }

    /* Trends button styling */
    .trends-button {
       display: inline-flex;
        align-items: center;
        gap: 0.6rem;
        background: #000000;
        color: #FFD700;
         padding: 0.8rem 1.5rem;
        border-radius: 25px;
        text-decoration: none;
        font-size: 0.95rem;
        font-weight: 600;
      border: 2px solid #333333;
       transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.4);
        animation: trendsFloat 3s ease-in-out infinite;
    cursor: pointer;
    }

    @keyframes trendsFloat {
       0%, 100% { transform: translateY(0px); }
       50% { transform: translateY(-2px); }
    }

    .trends-button:hover {
        transform: translateY(-3px) scale(1.05);
         box-shadow: 0 8px 25px rgba(0, 0, 0, 0.6);
        background: #1a1a1a;
       border-color: #FFD700;
       text-decoration: none;
        color: #FFD700;
    animation-play-state: paused;
    }

   .trends-button i {
     font-size: 1.1rem;
     transition: transform 0.3s ease;
    }

    .trends-button:hover i {
       transform: rotate(15deg) scale(1.1);
       color: #FFD700;
    }
    

    
    /* Responsive adjustments */
    @media (max-width: 768px) {
        /* Mobile adjustments for product boxes */
        .stColumns > div {
            width: 100% !important;
            max-width: 100% !important;
            margin-bottom: 2.5rem;
            padding: 0 !important;
        }
        
        .stColumns {
            flex-direction: column;
            gap: 2rem !important;
        }
        
        .product-box {
            height: 380px;
            margin-bottom: 2rem;
            padding: 1.5rem;
        }
        
        .product-image-container {
            height: 160px;
        }
        
        .main-title {
            font-size: 2.5rem !important;
            flex-direction: column;
            text-align: center;
        }
        
        .header-section {
            text-align: center;
        }
        
        .main .block-container {
            padding-left: 0.5rem; /* Further reduced for mobile */
            padding-right: 0.5rem; /* Further reduced for mobile */
        }
        
        /* Mobile shop buttons for recommended products - SMALLER SIZE HORIZONTALLY */
        .shop-buttons {
            flex-direction: column;
            gap: 0.6rem !important; /* Reduced gap for mobile vertical layout */
        }
        
        /* MOBILE RECOMMENDED PRODUCT BUTTONS - SMALLER HORIZONTALLY */
        .shop-btn {
            padding: 0.35rem 0.5rem !important; /* Reduced horizontal padding from 0.8rem to 0.5rem */
            font-size: 0.7rem !important; /* Slightly smaller font */
            min-width: 65px !important; /* Reduced from 80px */
            gap: 0.2rem !important; /* Reduced gap between icon and text */
        }
        
        .product-header {
            flex-direction: column;
            gap: 0.5rem;
            align-items: flex-start;
        }
        
        /* Mobile adjustments for description box */
        .about-section {
            margin: 2rem 0 !important;
            padding: 1.5rem 1.8rem !important;
            font-size: 1.1rem !important;
        }
        
        /* Mobile adjustments for sample items */
        .sample-grid {
            gap: 1.5rem 1.5rem;
            margin-top: 2rem;
            margin-bottom: 2rem;
            grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
        }
        
        .sample-item {
            height: 260px;
            padding: 1rem;
        }
        
        .sample-item-image {
            height: 130px;
        }
        
        .sample-item-text {
            font-size: 0.8rem;
        }
        
        /* Mobile sample item price */
        .sample-item .price-tag {
            font-size: 1.1rem !important;
            margin: 0.6rem 0 !important;
        }
        
        /* Mobile sample item shop buttons */
        .sample-item .shop-buttons {
            gap: 2rem !important;
        }
        
        /* Mobile icon size adjustment for recommended products - SMALLER SIZE */
        .shop-btn i {
            font-size: 0.8rem !important; /* Further reduced for mobile */
        }

        /* Mobile sample item icons */
        .sample-item .fab,
        .sample-item .fas {
            font-size: 1.3rem !important;
        }

        /* Mobile trends button */
        .trends-button {
            font-size: 0.9rem;
            padding: 0.7rem 1.3rem;
        }
        
        /* Mobile file uploader - ADJUSTED FOR INCREASED WIDTH */
        .stFileUploader {
            padding: 1.5rem;
            margin: 2.5rem -0.5rem; /* Adjusted negative margin for mobile */
            width: calc(100% + 1rem) !important; /* Adjusted width for mobile */
            max-width: calc(100% + 1rem) !important;
        }
    }
    
    /* Info and warning styling */
    .stInfo, .stWarning, .stError {
        background: rgba(255, 255, 255, 0.04) !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 10px !important;
        color: #ffffff !important;
        backdrop-filter: blur(10px) !important;
        animation: infoFloat 5s ease-in-out infinite;
        margin: 1.5rem 0 !important;
    }
    
    @keyframes infoFloat {
        0%, 100% { transform: translateY(0px); }
        50% { transform: translateY(-1px); }
    }
</style>
            
""", unsafe_allow_html=True)

# Set device
device = "cuda" if torch.cuda.is_available() else "cpu"

# Load CLIP model
@st.cache_resource
def load_model():
    model, preprocess = clip.load("ViT-B/32", device=device)
    return model, preprocess

model, preprocess = load_model()

# Function to convert image to base64
def image_to_base64(image_path):
    """Convert image to base64 string for HTML display"""
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()

# Function to convert uploaded file to base64
def uploaded_file_to_base64(uploaded_file):
    """Convert uploaded file to base64 string for HTML display"""
    return base64.b64encode(uploaded_file.read()).decode()

# Mock price and URL generator (replace with real data)
def generate_product_info(image_path):
    """Generate mock product information - replace with real product data"""
    filename = os.path.basename(image_path).lower()
    
    # Mock price generation based on filename patterns
    if any(word in filename for word in ['shoe', 'sneaker', 'boot']):
        price = random.randint(1500, 8000)
        category = 'footwear'
    elif any(word in filename for word in ['shirt', 'tshirt', 'top', 'dress']):
        price = random.randint(800, 3000)
        category = 'clothing'
    elif any(word in filename for word in ['watch', 'clock']):
        price = random.randint(2000, 15000)
        category = 'accessories'
    elif any(word in filename for word in ['phone', 'mobile', 'smartphone']):
        price = random.randint(10000, 50000)
        category = 'electronics'
    else:
        price = random.randint(500, 5000)
        category = 'general'
    
    # Generate mock URLs (replace with real product URLs)
    product_name = filename.replace('.jpg', '').replace('.png', '').replace('.jpeg', '')
    amazon_url = f"https://amazon.in/s?k={product_name.replace('_', '+')}"
    flipkart_url = f"https://flipkart.com/search?q={product_name.replace('_', '%20')}"
    
    return price, amazon_url, flipkart_url

# Load and preprocess product images
@st.cache_resource
def load_product_images(folder_path="product_images"):
    if not os.path.exists(folder_path):
        st.error(f"❌ Folder '{folder_path}' not found. Please create the folder and add product images.")
        return [], np.array([])
    
    image_paths = [os.path.join(folder_path, fname) for fname in os.listdir(folder_path)
                   if fname.lower().endswith(('.jpg', '.png', '.jpeg'))]
    
    if not image_paths:
        st.error(f"❌ No image files found in '{folder_path}' folder. Please add some product images.")
        return [], np.array([])
    
    features = []
    valid_image_paths = []

    for path in image_paths:
        try:
            img = Image.open(path).convert("RGB")
            image = preprocess(img).unsqueeze(0).to(device)
            with torch.no_grad():
                feat = model.encode_image(image)
            # Fix: Use keepdim=True instead of keepdims=True for PyTorch
            feat /= feat.norm(dim=-1, keepdim=True)
            features.append(feat.cpu().numpy()[0])
            valid_image_paths.append(path)
        except Exception as e:
            st.warning(f"⚠️ Skipped image '{os.path.basename(path)}' due to error: {e}")

    if not features:
        st.error("❌ No valid product images could be processed.")
        return [], np.array([])

    features_array = np.array(features)

    if features_array.ndim == 1:
        features_array = features_array.reshape(1, -1)

    return valid_image_paths, features_array

# Load images and features
image_paths, features_array = load_product_images()

# Check if any features were loaded
if features_array.size == 0:
    st.error("❌ No valid product images found in 'product_images' folder.")
    st.info("💡 **To fix this issue:**\n1. Create a folder named 'product_images' in your project directory\n2. Add product images (.jpg, .jpeg, .png) to this folder\n3. Restart the application")
    st.stop()

# Build FAISS index
feature_dim = features_array.shape[1]
index = faiss.IndexFlatL2(feature_dim)
index.add(features_array)

# Create main layout - Left header, Right upload
main_col1, main_col2 = st.columns([2, 1], gap="large")

# Left column - Header and About
with main_col1:
    st.markdown("""
    <div class="header-section">
        <div class="main-title">
            <i class="fas fa-shopping-bag title-icon icon"></i>
            Pic2Pick
        </div>
        <div class="tagline">
            See It. Snap It. Get It.
        </div>
        <div class="about-section">
            Welcome to <strong>Pic2Pick</strong> – your AI-powered visual shopping assistant. Tired of typing long product names or searching endlessly? Just upload a photo of what you like, and let our smart recommender instantly find visually similar items for you.
        </div>
    </div>
    """, unsafe_allow_html=True)

# Right column - Upload section
with main_col2:
    st.markdown('<div class="upload-section">', unsafe_allow_html=True)
    
    uploaded_file = st.file_uploader(
        "", 
        type=["jpg", "jpeg", "png"],
        help="Upload a clear image of the product you're looking for",
        label_visibility="collapsed"
    )
    
    # Add custom label with icon
    st.markdown("""
    <div style="text-align: center; margin-bottom: 1rem; color: #ffffff;">
        <i class="fas fa-cloud-upload-alt" style="font-size: 1.5rem; margin-right: 0.5rem;"></i>
        <strong>Upload Your Product Image</strong>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

if uploaded_file:
    # Create responsive layout for results
    result_col1, result_col2 = st.columns([3, 1], gap="large")
    
    try:
        img = Image.open(uploaded_file).convert("RGB")
        query_image = preprocess(img).unsqueeze(0).to(device)

        with torch.no_grad():
            query_feat = model.encode_image(query_image)
        # Fix: Use keepdim=True instead of keepdims=True for PyTorch
        query_feat /= query_feat.norm(dim=-1, keepdim=True)

        query_vector = query_feat.cpu().numpy()

        if query_vector.ndim == 1:
            query_vector = query_vector.reshape(1, -1)

        D, I = index.search(query_vector, k=20)

        # Filter results with 40% or higher similarity
        filtered_results = []
        for i, (distance, idx) in enumerate(zip(D[0], I[0])):
            similarity_score = 1 - distance
            if similarity_score >= 0.40:
                filtered_results.append((idx, similarity_score))
        
        # Right column - Upload preview
        with result_col2:
            # Convert uploaded file to base64 for HTML display
            uploaded_file.seek(0)  # Reset file pointer
            upload_base64 = uploaded_file_to_base64(uploaded_file)
            uploaded_file.seek(0)  # Reset again for processing
            
            st.markdown(f"""
            <div class="upload-preview">
                <h4><i class="fas fa-camera icon"></i> Your Upload</h4>
                <div class="upload-image-container">
                    <img src="data:image/jpeg;base64,{upload_base64}" alt="Uploaded Image">
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        # Left column - Recommendations in uniform grid
        with result_col1:
            if filtered_results:
                # Create 2xn grid with uniform boxes
                num_results = len(filtered_results)
                rows = (num_results + 1) // 2
                
                for row in range(rows):
                    cols = st.columns(2, gap="medium")
                    for col_idx in range(2):
                        result_idx = row * 2 + col_idx
                        if result_idx < num_results:
                            idx, similarity_score = filtered_results[result_idx]
                            with cols[col_idx]:
                                img_path = image_paths[idx]
                                price, amazon_url, flipkart_url = generate_product_info(img_path)
                                
                                # Get base64 encoded image
                                img_base64 = image_to_base64(img_path)
                                
                                # Create uniform product box with updated layout
                                st.markdown(f"""
                                <div class="product-box">
                                    <div class="product-header">
                                        <div class="product-title">
                                            <i class="fas fa-gift icon"></i> Recommended Product
                                        </div>
                                        <div class="similarity-badge-header">{similarity_score:.1%}</div>
                                    </div>
                                    <div class="product-image-container">
                                        <img src="data:image/jpeg;base64,{img_base64}" alt="Product">
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
            else:
                st.warning("🔍 No products found with 40% or higher similarity. Try a different image!")

    except Exception as e:
        st.error(f"❌ Failed to process uploaded image: {e}")

else:
    # Show sample products in enhanced grid
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
                        price, amazon_url, flipkart_url = generate_product_info(img_path)
                        
                        # Get base64 encoded image
                        img_base64 = image_to_base64(img_path)
                        
                        # Create sample product card
                        st.markdown(f"""
                        <div class="sample-item">
                            <div style="height: 120px; display: flex; align-items: center; justify-content: center; margin-bottom: 0.5rem;">
                                <img src="data:image/jpeg;base64,{img_base64}" 
                                     alt="Sample Product" 
                                     style="max-width: 100%; max-height: 100%; object-fit: contain; border-radius: 8px;">
                            </div>
                            <div style="color: #fbbf24; font-weight: 600; font-size: 0.9rem;">₹{price:,}</div>
                            <div style="display: flex; gap: 0.3rem; justify-content: center; margin-top: 0.5rem;">
                                <a href="{amazon_url}" target="_blank" style="color: #ff9900; text-decoration: none; font-size: 0.7rem;">
                                    <i class="fab fa-amazon"></i>
                                </a>
                                <a href="{flipkart_url}" target="_blank" style="color: #2874f0; text-decoration: none; font-size: 0.7rem;">
                                    <i class="fas fa-shopping-cart"></i>
                                </a>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
        
        # Call to action section
        st.markdown("""
        <div style="text-align: center; margin: 3rem 0 2rem 0;">
            <div style="background: rgba(59, 130, 246, 0.1); border: 1px solid rgba(59, 130, 246, 0.2); 
                        border-radius: 15px; padding: 2rem; backdrop-filter: blur(10px);">
                <h4 style="color: #ffffff; margin-bottom: 1rem; font-weight: 600;">
                    <i class="fas fa-magic icon" style="color: #3b82f6; margin-right: 0.5rem;"></i>
                    Ready to Find Your Perfect Match?
                </h4>
                <p style="color: #d1d5db; margin-bottom: 1.5rem;">
                    Upload an image of any product you like, and our AI will instantly find visually similar items from our catalog.
                </p>
                <div style="display: flex; justify-content: center; gap: 1rem; flex-wrap: wrap;">
                    <div style="background: rgba(34, 197, 94, 0.1); padding: 0.8rem 1.2rem; border-radius: 10px; 
                                border: 1px solid rgba(34, 197, 94, 0.2);">
                        <i class="fas fa-check-circle" style="color: #22c55e; margin-right: 0.5rem;"></i>
                        <span style="color: #ffffff; font-size: 0.9rem;">AI-Powered Matching</span>
                    </div>
                    <div style="background: rgba(168, 85, 247, 0.1); padding: 0.8rem 1.2rem; border-radius: 10px; 
                                border: 1px solid rgba(168, 85, 247, 0.2);">
                        <i class="fas fa-bolt" style="color: #a855f7; margin-right: 0.5rem;"></i>
                        <span style="color: #ffffff; font-size: 0.9rem;">Instant Results</span>
                    </div>
                    <div style="background: rgba(249, 115, 22, 0.1); padding: 0.8rem 1.2rem; border-radius: 10px; 
                                border: 1px solid rgba(249, 115, 22, 0.2);">
                        <i class="fas fa-shopping-bag" style="color: #f97316; margin-right: 0.5rem;"></i>
                        <span style="color: #ffffff; font-size: 0.9rem;">Direct Shopping Links</span>
                    </div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
    else:
        # Fallback when no images are available
        st.markdown("""
        <div style="text-align: center; margin: 4rem 0;">
            <div style="background: rgba(239, 68, 68, 0.1); border: 1px solid rgba(239, 68, 68, 0.2); 
                        border-radius: 15px; padding: 3rem; backdrop-filter: blur(10px);">
                <i class="fas fa-exclamation-triangle" style="font-size: 3rem; color: #ef4444; margin-bottom: 1rem;"></i>
                <h3 style="color: #ffffff; margin-bottom: 1rem;">No Product Images Found</h3>
                <p style="color: #d1d5db; margin-bottom: 2rem; max-width: 600px; margin-left: auto; margin-right: auto;">
                    To use Pic2Pick, you need to set up a product catalog first. Follow these simple steps:
                </p>
                <div style="text-align: left; max-width: 500px; margin: 0 auto;">
                    <div style="background: rgba(255, 255, 255, 0.04); padding: 1rem; border-radius: 10px; margin-bottom: 1rem;">
                        <strong style="color: #3b82f6;">Step 1:</strong> 
                        <span style="color: #d1d5db;">Create a folder named 'product_images' in your project directory</span>
                    </div>
                    <div style="background: rgba(255, 255, 255, 0.04); padding: 1rem; border-radius: 10px; margin-bottom: 1rem;">
                        <strong style="color: #3b82f6;">Step 2:</strong> 
                        <span style="color: #d1d5db;">Add product images (.jpg, .jpeg, .png) to this folder</span>
                    </div>
                    <div style="background: rgba(255, 255, 255, 0.04); padding: 1rem; border-radius: 10px;">
                        <strong style="color: #3b82f6;">Step 3:</strong> 
                        <span style="color: #d1d5db;">Restart the application to load your product catalog</span>
                    </div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)


# Render footer component
render_footer()
