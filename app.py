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

# Enhanced CSS with black background and teal green blur on left
st.markdown("""
<style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Main app background - solid black */
    .stApp {
        background: #000000;
        background-attachment: fixed;
        font-family: 'Inter', sans-serif;
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
    }
    
    /* Title styling */
    .stTitle {
        color: #ffffff !important;
        text-align: center;
        font-weight: 700 !important;
        font-size: 3rem !important;
        margin-bottom: 0.5rem !important;
        text-shadow: 0 0 20px rgba(0, 188, 212, 0.5);
    }
    
    /* Subtitle styling */
    .stMarkdown p {
        color: #e0e0e0 !important;
        text-align: center;
    }
    
    /* Enhanced file uploader */
    .stFileUploader {
        background: linear-gradient(135deg, rgba(0, 188, 212, 0.1), rgba(255, 193, 7, 0.1));
        border: 2px dashed rgba(0, 188, 212, 0.5);
        border-radius: 15px;
        padding: 2rem;
        text-align: center;
        margin: 2rem 0;
        transition: all 0.3s ease;
    }
    
    .stFileUploader:hover {
        border-color: rgba(0, 188, 212, 0.8);
        background: linear-gradient(135deg, rgba(0, 188, 212, 0.15), rgba(255, 193, 7, 0.15));
        transform: translateY(-2px);
        box-shadow: 0 10px 30px rgba(0, 188, 212, 0.2);
    }
    
    .stFileUploader label {
        color: #ffffff !important;
        font-size: 1.2rem !important;
        font-weight: 500 !important;
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
        transition: all 0.3s ease;
        backdrop-filter: blur(10px);
    }
    
    .product-box:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 40px rgba(0, 188, 212, 0.2);
        border-color: rgba(0, 188, 212, 0.3);
    }
    
    .product-header {
        text-align: center;
        margin-bottom: 1rem;
        color: #ffffff;
        font-weight: 600;
        font-size: 1rem;
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
    }
    
    .product-image-container img {
        max-width: 100%;
        max-height: 100%;
        object-fit: contain;
        border-radius: 8px;
    }
    
    .product-info {
        text-align: center;
        margin-top: auto;
    }
    
    .similarity-badge {
        background: linear-gradient(135deg, #00bcd4, #4caf50);
        color: white;
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
        margin-bottom: 0.5rem;
        display: inline-block;
    }
    
    .price-tag {
        color: #ffc107;
        font-size: 1.1rem;
        font-weight: 600;
        margin: 0.5rem 0;
    }
    
    .shop-buttons {
        display: flex;
        gap: 0.5rem;
        justify-content: center;
        margin-top: 0.5rem;
    }
    
    .shop-btn {
        background: linear-gradient(135deg, #ff6b6b, #ee5a24);
        color: white !important;
        padding: 0.4rem 0.8rem;
        border-radius: 8px;
        text-decoration: none !important;
        font-size: 0.8rem;
        font-weight: 500;
        transition: all 0.3s ease;
        border: none;
        cursor: pointer;
    }
    
    .shop-btn:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(255, 107, 107, 0.3);
        text-decoration: none !important;
        color: white !important;
    }
    
    .shop-btn.flipkart {
        background: linear-gradient(135deg, #2874f0, #1e60d1);
    }
    
    .shop-btn.flipkart:hover {
        box-shadow: 0 8px 20px rgba(40, 116, 240, 0.3);
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
    }
    
    .upload-preview h4 {
        color: #ffffff;
        margin-bottom: 1rem;
        font-weight: 600;
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
        
        .stTitle {
            font-size: 2rem !important;
        }
        
        .main .block-container {
            padding-left: 1rem;
            padding-right: 1rem;
        }
        
        .shop-buttons {
            flex-direction: column;
            gap: 0.3rem;
        }
    }
    
    /* Info and warning styling */
    .stInfo, .stWarning, .stError {
        background: rgba(255, 255, 255, 0.05) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 10px !important;
        color: #ffffff !important;
        backdrop-filter: blur(10px) !important;
    }
    
    /* Sample products styling */
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
    }
    
    .sample-item:hover {
        transform: translateY(-3px);
        box-shadow: 0 10px 25px rgba(255, 193, 7, 0.2);
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
    image_paths = [os.path.join(folder_path, fname) for fname in os.listdir(folder_path)
                   if fname.lower().endswith(('.jpg', '.png', '.jpeg'))]
    
    features = []
    valid_image_paths = []

    for path in image_paths:
        try:
            img = Image.open(path).convert("RGB")
            image = preprocess(img).unsqueeze(0).to(device)
            with torch.no_grad():
                feat = model.encode_image(image)
            feat /= feat.norm(dim=-1, keepdim=True)
            features.append(feat.cpu().numpy()[0])
            valid_image_paths.append(path)
        except Exception as e:
            st.warning(f"⚠️ Skipped image '{os.path.basename(path)}' due to error: {e}")

    features_array = np.array(features)

    if features_array.ndim == 1:
        features_array = features_array.reshape(1, -1)

    return valid_image_paths, features_array

# Load images and features
image_paths, features_array = load_product_images()

# Check if any features were loaded
if features_array.size == 0:
    st.error("❌ No valid product images found in 'product_images' folder.")
    st.stop()

# Build FAISS index
feature_dim = features_array.shape[1]
index = faiss.IndexFlatL2(feature_dim)
index.add(features_array)

# App Header
st.title("🛍️ Pic2Pick")
st.markdown("**Visual Product Recommender** - Upload a product image and discover visually similar items!")

# Enhanced file uploader
uploaded_file = st.file_uploader(
    "🖼️ Drag and drop your image here or click to browse", 
    type=["jpg", "jpeg", "png"],
    help="Upload a clear image of the product you're looking for"
)

if uploaded_file:
    # Create responsive layout
    col1, col2 = st.columns([3, 1], gap="large")
    
    try:
        img = Image.open(uploaded_file).convert("RGB")
        query_image = preprocess(img).unsqueeze(0).to(device)

        with torch.no_grad():
            query_feat = model.encode_image(query_image)
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
        with col2:
            # Convert uploaded file to base64 for HTML display
            uploaded_file.seek(0)  # Reset file pointer
            upload_base64 = uploaded_file_to_base64(uploaded_file)
            uploaded_file.seek(0)  # Reset again for processing
            
            st.markdown(f"""
            <div class="upload-preview">
                <h4>📸 Your Upload</h4>
                <div class="upload-image-container">
                    <img src="data:image/jpeg;base64,{upload_base64}" alt="Uploaded Image">
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        # Left column - Recommendations in uniform grid
        with col1:
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
                                
                                # Create uniform product box with everything inside
                                st.markdown(f"""
                                <div class="product-box">
                                    <div class="product-header">
                                        🛍️ Recommended Product
                                    </div>
                                    <div class="product-image-container">
                                        <img src="data:image/jpeg;base64,{img_base64}" alt="Product">
                                    </div>
                                    <div class="product-info">
                                        <div class="similarity-badge">{similarity_score:.1%} match</div>
                                        <div class="price-tag">₹{price:,}</div>
                                        <div class="shop-buttons">
                                            <a href="{amazon_url}" target="_blank" class="shop-btn">🛒 Amazon</a>
                                            <a href="{flipkart_url}" target="_blank" class="shop-btn flipkart">🛍️ Flipkart</a>
                                        </div>
                                    </div>
                                </div>
                                """, unsafe_allow_html=True)
            else:
                st.warning("🔍 No products found with 40% or higher similarity. Try a different image!")

    except Exception as e:
        st.error(f"❌ Failed to process uploaded image: {e}")

else:
    # Enhanced placeholder when no image is uploaded
    st.info("👆 Upload an image above to get started!")
    
    # Show sample products in enhanced grid
    if len(image_paths) > 0:
        st.markdown("**✨ Sample Products Available:**")
        
        sample_cols = st.columns(4, gap="small")
        for i, col in enumerate(sample_cols):
            if i < min(4, len(image_paths)):
                with col:
                    st.markdown('<div class="sample-item">', unsafe_allow_html=True)
                    st.image(image_paths[i], caption=f"Product {i+1}", width=120)
                    st.markdown('</div>', unsafe_allow_html=True)

render_footer()