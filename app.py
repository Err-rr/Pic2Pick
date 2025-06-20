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
    
    /* Main app background with image overlay */
    .stApp {
        background: 
            linear-gradient(rgba(0, 0, 0, 0.85), rgba(0, 0, 0, 0.85)),
            url('https://i.pinimg.com/736x/bf/b9/6f/bfb96f612ae8729f5ef4ab999faec2f6.jpg');
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
        font-family: 'Inter', sans-serif;
        animation: backgroundFloat 20s ease-in-out infinite;
    }
    
    @keyframes backgroundFloat {
        0%, 100% { background-position: center center; }
        50% { background-position: center 10px; }
    }
    
    /* Add teal green blur overlay on left side */
    .stApp::before {
        content: '';
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: 
            radial-gradient(circle at 20% 50%, rgba(20, 184, 166, 0.3) 0%, transparent 50%),
            radial-gradient(circle at 10% 30%, rgba(45, 212, 191, 0.25) 0%, transparent 40%),
            radial-gradient(circle at 15% 70%, rgba(56, 178, 172, 0.2) 0%, transparent 35%);
        filter: blur(100px);
        z-index: -1;
        pointer-events: none;
        animation: blurFloat 15s ease-in-out infinite;
    }
    
    @keyframes blurFloat {
        0%, 100% { opacity: 0.8; }
        50% { opacity: 0.6; }
    }
    
    /* Main container adjustments */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        padding-left: 1.5rem;
        padding-right: 1.5rem;
        background: rgba(0, 0, 0, 0.3);
        backdrop-filter: blur(10px);
        border-radius: 20px;
        margin-top: 1rem;
        border: 1px solid rgba(255, 255, 255, 0.1);
        animation: containerFloat 10s ease-in-out infinite;
    }
    
    @keyframes containerFloat {
        0%, 100% { transform: translateY(0px); }
        50% { transform: translateY(-5px); }
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
    
    /* Title styling - removed glow effect */
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
        color: #14b8a6; /* Teal green color */
        animation: iconBounce 2s ease-in-out infinite;
    }
    
    @keyframes iconBounce {
        0%, 100% { transform: translateY(0px); }
        50% { transform: translateY(-10px); }
    }
    
    /* Tagline styling - changed to teal green */
    .tagline {
        color: #14b8a6 !important; /* Teal green color */
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
        color: #e0e0e0 !important;
        font-size: 1.1rem !important;
        line-height: 1.6 !important;
        margin-bottom: 2rem !important;
        animation: fadeInUp 1.5s ease-out 1s both;
    }
    
    /* Upload section styling */
    .upload-section {
        animation: slideInRight 1s ease-out;
    }
    
    @keyframes slideInRight {
        from { opacity: 0; transform: translateX(50px); }
        to { opacity: 1; transform: translateX(0); }
    }
    
    /* Enhanced file uploader */
    .stFileUploader {
        background: linear-gradient(135deg, rgba(20, 184, 166, 0.1), rgba(255, 193, 7, 0.1));
        border: 2px dashed rgba(20, 184, 166, 0.5);
        border-radius: 15px;
        padding: 2rem;
        text-align: center;
        margin: 2rem 0;
        transition: all 0.3s ease;
        animation: pulseGlow 4s ease-in-out infinite;
    }
    
    @keyframes pulseGlow {
        0%, 100% { box-shadow: 0 0 20px rgba(20, 184, 166, 0.2); }
        50% { box-shadow: 0 0 40px rgba(20, 184, 166, 0.4); }
    }
    
    .stFileUploader:hover {
        border-color: rgba(20, 184, 166, 0.8);
        background: linear-gradient(135deg, rgba(20, 184, 166, 0.15), rgba(255, 193, 7, 0.15));
        transform: translateY(-5px) scale(1.02);
        box-shadow: 0 15px 40px rgba(20, 184, 166, 0.3);
        animation-play-state: paused;
    }
    
    .stFileUploader label {
        color: #ffffff !important;
        font-size: 1.2rem !important;
        font-weight: 500 !important;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 0.5rem;
    }
    
    /* Uniform product boxes */
    .product-box {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 15px;
        padding: 1rem;
        margin-bottom: 1rem;
        height: 400px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        transition: all 0.4s ease;
        backdrop-filter: blur(10px);
        animation: productFloat 6s ease-in-out infinite;
        position: relative;
    }
    
    @keyframes productFloat {
        0%, 100% { transform: translateY(0px); }
        50% { transform: translateY(-3px); }
    }
    
    .product-box:hover {
        transform: translateY(-10px) scale(1.03);
        box-shadow: 0 20px 50px rgba(20, 184, 166, 0.3); /* Changed to teal green */
        border-color: rgba(20, 184, 166, 0.5);
        background: rgba(255, 255, 255, 0.08);
        animation-play-state: paused;
    }
    
    /* Updated product header - split layout */
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
        background: linear-gradient(135deg, #14b8a6, #059669); /* Teal green gradient */
        color: white;
        padding: 0.2rem 0.6rem;
        border-radius: 15px;
        font-size: 0.75rem;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .product-box:hover .similarity-badge-header {
        transform: scale(1.05);
        box-shadow: 0 3px 10px rgba(20, 184, 166, 0.2); /* Reduced glow */
    }
    
    .product-image-container {
        height: 200px;
        display: flex;
        align-items: center;
        justify-content: center;
        overflow: hidden;
        border-radius: 10px;
        background: rgba(255, 255, 255, 0.02);
        margin-bottom: 1rem;
        transition: all 0.3s ease;
    }
    
    .product-box:hover .product-image-container {
        background: rgba(255, 255, 255, 0.05);
        transform: scale(1.05);
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
        color: #ffc107;
        font-size: 1.1rem;
        font-weight: 600;
        margin: 0.5rem 0;
        transition: all 0.3s ease;
    }
    
    .product-box:hover .price-tag {
        color: #ffeb3b;
        transform: scale(1.05);
    }
    
    .shop-buttons {
        display: flex;
        gap: 0.5rem;
        justify-content: center;
        margin-top: 0.5rem;
    }
    
    /* Enhanced shop buttons with cool icons and design */
    .shop-btn {
        color: white !important;
        padding: 0.5rem 1rem;
        border-radius: 12px;
        text-decoration: none !important;
        font-size: 0.85rem;
        font-weight: 600;
        transition: all 0.3s ease;
        border: none;
        cursor: pointer;
        display: flex;
        align-items: center;
        gap: 0.4rem;
        position: relative;
        overflow: hidden;
        min-width: 90px;
        justify-content: center;
    }
    
    .shop-btn::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
        transition: left 0.5s;
    }
    
    .shop-btn:hover::before {
        left: 100%;
    }
    
    .shop-btn:hover {
        transform: translateY(-3px) scale(1.05);
        text-decoration: none !important;
        color: white !important;
    }
    
    .shop-btn.amazon {
        background: linear-gradient(135deg, #ff9900, #ff7700);
        box-shadow: 0 4px 15px rgba(255, 153, 0, 0.3);
    }
    
    .shop-btn.amazon:hover {
        box-shadow: 0 8px 25px rgba(255, 153, 0, 0.5);
        background: linear-gradient(135deg, #ffaa00, #ff8800);
    }
    
    .shop-btn.flipkart {
        background: linear-gradient(135deg, #2874f0, #1e60d1);
        box-shadow: 0 4px 15px rgba(40, 116, 240, 0.3);
    }
    
    .shop-btn.flipkart:hover {
        box-shadow: 0 8px 25px rgba(40, 116, 240, 0.5);
        background: linear-gradient(135deg, #3484ff, #2571ee);
    }
    
    /* Icon styling for buttons */
    .shop-btn i {
        font-size: 1rem;
        transition: transform 0.3s ease;
    }
    
    .shop-btn:hover i {
        transform: scale(1.2) rotate(5deg);
    }
    
    /* Upload preview box */
    .upload-preview {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 15px;
        padding: 1.5rem;
        text-align: center;
        backdrop-filter: blur(10px);
        height: 400px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        transition: all 0.3s ease;
        animation: previewFloat 8s ease-in-out infinite;
    }
    
    @keyframes previewFloat {
        0%, 100% { transform: translateY(0px); }
        50% { transform: translateY(-5px); }
    }
    
    .upload-preview:hover {
        transform: translateY(-5px) scale(1.02);
        box-shadow: 0 15px 35px rgba(20, 184, 166, 0.2);
        border-color: rgba(20, 184, 166, 0.3);
    }
    
    .upload-preview h4 {
        color: #ffffff;
        margin-bottom: 1rem;
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
        transform: scale(1.05);
        box-shadow: 0 10px 30px rgba(20, 184, 166, 0.3);
    }
    
    /* Sample products styling - removed horizontal bars */
    .sample-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
        gap: 1rem;
        margin-top: 1rem;
    }
    
    .sample-item {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 10px;
        padding: 0.8rem;
        text-align: center;
        transition: all 0.3s ease;
        animation: sampleFloat 7s ease-in-out infinite;
        border: 1px solid rgba(255, 255, 255, 0.05);
    }
    
    @keyframes sampleFloat {
        0%, 100% { transform: translateY(0px); }
        50% { transform: translateY(-2px); }
    }
    
    .sample-item:hover {
        transform: translateY(-8px) scale(1.05);
        box-shadow: 0 15px 30px rgba(20, 184, 166, 0.3); /* Changed to teal green */
        background: rgba(255, 255, 255, 0.08);
        border-color: rgba(20, 184, 166, 0.3);
        animation-play-state: paused;
    }
    
    /* Remove borders from sample images */
    .sample-item img {
        border: none !important;
        border-radius: 8px;
    }
    
    /* Icon styling */
    .icon {
        transition: all 0.3s ease;
    }
    
    .icon:hover {
        transform: rotate(360deg) scale(1.2);
    }
    
    /* Responsive adjustments */
    @media (max-width: 768px) {
        .stColumns > div {
            width: 100% !important;
            margin-bottom: 1rem;
        }
        
        .stColumns {
            flex-direction: column;
        }
        
        .product-box {
            height: 350px;
        }
        
        .product-image-container {
            height: 150px;
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
            padding-left: 1rem;
            padding-right: 1rem;
        }
        
        .shop-buttons {
            flex-direction: column;
            gap: 0.3rem;
        }
        
        .product-header {
            flex-direction: column;
            gap: 0.3rem;
            align-items: flex-start;
        }
    }
    
    /* Info and warning styling */
    .stInfo, .stWarning, .stError {
        background: rgba(255, 255, 255, 0.05) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 10px !important;
        color: #ffffff !important;
        backdrop-filter: blur(10px) !important;
        animation: infoFloat 5s ease-in-out infinite;
    }
    
    @keyframes infoFloat {
        0%, 100% { transform: translateY(0px); }
        50% { transform: translateY(-2px); }
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
    # Show sample products in enhanced grid - removed the "Upload an image" text
    if len(image_paths) > 0:
        st.markdown("""
        <div style="text-align: center; margin: 3rem 0;">
            <h3 style="color: #ffffff; font-weight: 600; margin-bottom: 0.5rem;">
                <i class="fas fa-star icon" style="color: #14b8a6; margin-right: 0.5rem;"></i>
                Featured Products
            </h3>
            <p style="color: #14b8a6; font-size: 1.1rem; font-weight: 500; margin-bottom: 2rem;">
                Discover our collection of trending items
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Show random sample of 8 products in a 4x2 grid
        sample_indices = random.sample(range(len(image_paths)), min(8, len(image_paths)))
        
        # Create 2 rows of 4 columns each
        for row in range(2):
            cols = st.columns(4, gap="medium")
            for col_idx in range(4):
                sample_idx = row * 4 + col_idx
                if sample_idx < len(sample_indices):
                    idx = sample_indices[sample_idx]
                    with cols[col_idx]:
                        img_path = image_paths[idx]
                        price, amazon_url, flipkart_url = generate_product_info(img_path)
                        
                        # Get base64 encoded image
                        img_base64 = image_to_base64(img_path)
                        product_name = os.path.basename(img_path).replace('.jpg', '').replace('.png', '').replace('.jpeg', '').replace('_', ' ').title()
                        
                        # Create sample product item
                        st.markdown(f"""
                        <div class="sample-item">
                            <div style="height: 120px; display: flex; align-items: center; justify-content: center; margin-bottom: 0.5rem;">
                                <img src="data:image/jpeg;base64,{img_base64}" 
                                     alt="{product_name}" 
                                     style="max-width: 100%; max-height: 100%; object-fit: contain; border-radius: 8px;">
                            </div>
                            <div style="color: #ffffff; font-size: 0.85rem; font-weight: 500; margin-bottom: 0.3rem;">
                                {product_name[:20]}{'...' if len(product_name) > 20 else ''}
                            </div>
                            <div style="color: #ffc107; font-size: 0.9rem; font-weight: 600; margin-bottom: 0.5rem;">
                                ₹{price:,}
                            </div>
                            <div style="display: flex; gap: 0.3rem; justify-content: center;">
                                <a href="{amazon_url}" target="_blank" 
                                   style="background: linear-gradient(135deg, #ff9900, #ff7700); color: white; 
                                          padding: 0.3rem 0.6rem; border-radius: 8px; text-decoration: none; 
                                          font-size: 0.7rem; font-weight: 600; transition: all 0.3s ease;
                                          display: flex; align-items: center; gap: 0.2rem;">
                                    <i class="fab fa-amazon" style="font-size: 0.8rem;"></i> Shop
                                </a>
                                <a href="{flipkart_url}" target="_blank" 
                                   style="background: linear-gradient(135deg, #2874f0, #1e60d1); color: white; 
                                          padding: 0.3rem 0.6rem; border-radius: 8px; text-decoration: none; 
                                          font-size: 0.7rem; font-weight: 600; transition: all 0.3s ease;
                                          display: flex; align-items: center; gap: 0.2rem;">
                                    <i class="fas fa-shopping-cart" style="font-size: 0.8rem;"></i> Buy
                                </a>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)

# Add some spacing before footer
st.markdown("<div style='height: 3rem;'></div>", unsafe_allow_html=True)

# Instructions section
st.markdown("""
<div style="background: rgba(255, 255, 255, 0.05); border-radius: 15px; padding: 2rem; margin: 2rem 0; 
            backdrop-filter: blur(10px); border: 1px solid rgba(255, 255, 255, 0.1);">
    <h4 style="color: #14b8a6; font-weight: 600; margin-bottom: 1rem; text-align: center;">
        <i class="fas fa-lightbulb icon" style="margin-right: 0.5rem;"></i>
        How to Use Pic2Pick
    </h4>
    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 1.5rem; margin-top: 1.5rem;">
        <div style="text-align: center; color: #e0e0e0;">
            <div style="background: rgba(20, 184, 166, 0.1); border-radius: 50%; width: 60px; height: 60px; 
                        display: flex; align-items: center; justify-content: center; margin: 0 auto 1rem;">
                <i class="fas fa-camera" style="font-size: 1.5rem; color: #14b8a6;"></i>
            </div>
            <h5 style="color: #ffffff; margin-bottom: 0.5rem;">1. Upload Image</h5>
            <p style="font-size: 0.9rem; line-height: 1.4;">Take or upload a clear photo of the product you want to find</p>
        </div>
        <div style="text-align: center; color: #e0e0e0;">
            <div style="background: rgba(20, 184, 166, 0.1); border-radius: 50%; width: 60px; height: 60px; 
                        display: flex; align-items: center; justify-content: center; margin: 0 auto 1rem;">
                <i class="fas fa-magic" style="font-size: 1.5rem; color: #14b8a6;"></i>
            </div>
            <h5 style="color: #ffffff; margin-bottom: 0.5rem;">2. AI Analysis</h5>
            <p style="font-size: 0.9rem; line-height: 1.4;">Our AI analyzes your image and finds visually similar products</p>
        </div>
        <div style="text-align: center; color: #e0e0e0;">
            <div style="background: rgba(20, 184, 166, 0.1); border-radius: 50%; width: 60px; height: 60px; 
                        display: flex; align-items: center; justify-content: center; margin: 0 auto 1rem;">
                <i class="fas fa-shopping-bag" style="font-size: 1.5rem; color: #14b8a6;"></i>
            </div>
            <h5 style="color: #ffffff; margin-bottom: 0.5rem;">3. Shop & Buy</h5>
            <p style="font-size: 0.9rem; line-height: 1.4;">Browse recommendations and shop directly from Amazon or Flipkart</p>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# Add footer
render_footer()

# Add some JavaScript for enhanced interactions
st.markdown("""
<script>
// Add smooth scrolling for better UX
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        document.querySelector(this.getAttribute('href')).scrollIntoView({
            behavior: 'smooth'
        });
    });
});

// Add loading animation for file upload
const fileUploader = document.querySelector('.stFileUploader');
if (fileUploader) {
    fileUploader.addEventListener('change', function() {
        const loader = document.createElement('div');
        loader.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Processing your image...';
        loader.style.cssText = `
            position: fixed; top: 50%; left: 50%; transform: translate(-50%, -50%);
            background: rgba(0,0,0,0.8); color: white; padding: 1rem 2rem;
            border-radius: 10px; z-index: 9999; font-size: 1.1rem;
        `;
        document.body.appendChild(loader);
        
        setTimeout(() => {
            if (document.body.contains(loader)) {
                document.body.removeChild(loader);
            }
        }, 3000);
    });
}

// Add parallax effect to background
window.addEventListener('scroll', () => {
    const scrolled = window.pageYOffset;
    const rate = scrolled * -0.5;
    document.querySelector('.stApp').style.transform = `translateY(${rate}px)`;
});

// Add hover sound effect (optional - can be removed if not needed)
const buttons = document.querySelectorAll('.shop-btn, .sample-item');
buttons.forEach(button => {
    button.addEventListener('mouseenter', () => {
        // Subtle scale effect on hover
        button.style.transform = 'scale(1.05)';
    });
    
    button.addEventListener('mouseleave', () => {
        button.style.transform = 'scale(1)';
    });
});
</script>
""", unsafe_allow_html=True)
