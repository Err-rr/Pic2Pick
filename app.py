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
        padding-left: 1rem;
        padding-right: 1rem;
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
        color: #3b82f6;
        animation: iconBounce 2s ease-in-out infinite;
    }
    
    @keyframes iconBounce {
        0%, 100% { transform: translateY(0px); }
        50% { transform: translateY(-8px); }
    }
    
    /* Tagline styling */
    .tagline {
        color: #60a5fa !important;
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
    
    /* Enhanced file uploader */
    .stFileUploader {
        background: #000000 !important;
        border: 2px dashed rgba(59, 130, 246, 0.4);
        border-radius: 15px;
        padding: 2rem;
        text-align: center;
        margin: 2.5rem 0;
        transition: all 0.3s ease;
        animation: uploadPulse 4s ease-in-out infinite;
        width: 100% !important;
        max-width: 100% !important;
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
    
    /* Product boxes */
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
            0 15px 35px rgba(59, 130, 246, 0.15),
            0 0 20px rgba(59, 130, 246, 0.08);
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
    
    /* Shop buttons */
    .shop-buttons {
        display: flex;
        gap: 1rem;
        justify-content: center;
        margin-top: 1rem;
    }
    
    .shop-btn {
        color: white !important;
        padding: 0.4rem 0.8rem !important;
        border-radius: 8px !important;
        text-decoration: none !important;
        font-size: 0.75rem !important;
        font-weight: 600;
        transition: all 0.3s ease;
        border: none;
        cursor: pointer;
        display: flex;
        align-items: center;
        gap: 0.3rem !important;
        position: relative;
        overflow: hidden;
        min-width: 80px !important;
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
    
    .shop-btn i {
        font-size: 1rem !important;
        transition: transform 0.3s ease;
    }
    
    .shop-btn:hover i {
        transform: scale(1.1) rotate(3deg);
    }
    
    /* Upload preview box */
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

    /* Category detection styling */
    .category-badge {
        background: linear-gradient(135deg, #22c55e, #16a34a);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 25px;
        font-size: 0.9rem;
        font-weight: 600;
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        margin: 1rem 0;
        animation: categoryPulse 2s ease-in-out infinite;
    }

    @keyframes categoryPulse {
        0%, 100% { box-shadow: 0 0 15px rgba(34, 197, 94, 0.3); }
        50% { box-shadow: 0 0 25px rgba(34, 197, 94, 0.5); }
    }

    /* Radio button styling */
    .stRadio {
        background: rgba(255, 255, 255, 0.04);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 10px;
        padding: 1rem;
        margin: 1rem 0;
    }

    .stRadio label {
        color: #ffffff !important;
        font-weight: 500;
    }

    /* Text input styling */
    .stTextInput input {
        background: #000000 !important;
        border: 2px solid rgba(59, 130, 246, 0.2) !important;
        color: #ffffff !important;
        border-radius: 10px !important;
        padding: 0.75rem 1rem !important;
        transition: all 0.3s ease;
    }

    .stTextInput input:focus {
        border-color: rgba(59, 130, 246, 0.7) !important;
        box-shadow: 0 0 20px rgba(59, 130, 246, 0.2) !important;
    }
    
    /* Responsive adjustments */
    @media (max-width: 768px) {
        .main-title {
            font-size: 2.5rem !important;
            flex-direction: column;
            text-align: center;
        }
        
        .header-section {
            text-align: center;
        }
        
        .main .block-container {
            padding-left: 0.5rem;
            padding-right: 0.5rem;
        }
        
        .product-box {
            height: 380px;
            margin-bottom: 2rem;
            padding: 1.5rem;
        }
        
        .product-image-container {
            height: 160px;
        }
        
        .shop-buttons {
            flex-direction: column;
            gap: 0.6rem !important;
        }
        
        .shop-btn {
            padding: 0.35rem 0.5rem !important;
            font-size: 0.7rem !important;
            min-width: 65px !important;
            gap: 0.2rem !important;
        }
        
        .shop-btn i {
            font-size: 0.8rem !important;
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
            <i class="fas fa-shopping-bag title-icon icon"></i>
            Pic2Pick
        </div>
        <div class="tagline">
            See It. Snap It. Get It.
        </div>
        <div class="about-section">
            Welcome to <strong>Pic2Pick</strong> – your AI-powered visual shopping assistant. Upload an image of any product you like, and our smart recommender will instantly find visually similar items from our catalog across multiple categories.
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
                        for idx in I[0]:
                            if idx >= len(best_urls):
                                continue
                            url = best_urls[idx]
                            if url not in shown_urls:
                                shown_urls.add(url)
                                found_url = url
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
                                    
                                    # Calculate similarity (mock calculation)
                                    similarity = 1 - (D[0][shown_count] / 2)  # Normalize to percentage
                                    
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

# Footer
st.markdown("""
<div style="margin-top: 4rem; padding: 2rem; text-align: center; color: #60a5fa; border-top: 1px solid rgba(255, 255, 255, 0.1);">
    <p style="font-size: 0.9rem; margin: 0;">
        <i class="fas fa-heart" style="color: #ef4444; margin: 0 0.5rem;"></i>
        Made with AI-powered visual search technology
        <i class="fas fa-heart" style="color: #ef4444; margin: 0 0.5rem;"></i>
    </p>
</div>
""", unsafe_allow_html=True)