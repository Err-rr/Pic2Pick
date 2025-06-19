import os
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

import streamlit as st
from PIL import Image
import os
import numpy as np
import torch
import clip
import faiss

# Set page config
st.set_page_config(
    page_title="Pic2Pick", 
    page_icon="🛍️", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for better responsiveness and compact layout
st.markdown("""
<style>
    /* Main container adjustments */
    .main .block-container {
        padding-top: 1rem;
        padding-bottom: 1rem;
        padding-left: 1rem;
        padding-right: 1rem;
    }
    
    /* Responsive column adjustments */
    @media (max-width: 768px) {
        .stColumns > div {
            width: 100% !important;
            margin-bottom: 1rem;
        }
        
        /* Stack columns vertically on mobile */
        .stColumns {
            flex-direction: column;
        }
        
        /* Adjust image sizes for mobile */
        .stImage > img {
            max-width: 150px !important;
            height: auto !important;
        }
    }
    
    @media (min-width: 769px) and (max-width: 1024px) {
        /* Tablet adjustments */
        .stImage > img {
            max-width: 160px !important;
        }
    }
    
    /* Compact spacing */
    .stImage {
        margin-bottom: 0.5rem !important;
    }
    
    .stMarkdown {
        margin-bottom: 0.5rem !important;
    }
    
    /* Better mobile navigation */
    @media (max-width: 640px) {
        .main .block-container {
            padding-left: 0.5rem;
            padding-right: 0.5rem;
        }
        
        .stTitle {
            font-size: 1.5rem !important;
        }
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

# Load and preprocess product images
@st.cache_resource
def load_product_images(folder_path="product_images"):
    image_paths = [os.path.join(folder_path, fname) for fname in os.listdir(folder_path)
                   if fname.lower().endswith(('.jpg', '.png', '.jpeg'))]
    
    features = []
    valid_image_paths = []

    for path in image_paths:
        try:
            img = Image.open(path).convert("RGB")  # Force RGB mode
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

# File uploader
uploaded_file = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png"])

if uploaded_file:
    # Create responsive layout - adjust column ratios based on screen size
    col1, col2 = st.columns([2.5, 1], gap="medium")
    
    try:
        img = Image.open(uploaded_file).convert("RGB")
        query_image = preprocess(img).unsqueeze(0).to(device)

        with torch.no_grad():
            query_feat = model.encode_image(query_image)
        query_feat /= query_feat.norm(dim=-1, keepdim=True)

        query_vector = query_feat.cpu().numpy()

        if query_vector.ndim == 1:
            query_vector = query_vector.reshape(1, -1)

        D, I = index.search(query_vector, k=20)  # Get more results to filter

        # Filter results with 40% or higher similarity
        filtered_results = []
        for i, (distance, idx) in enumerate(zip(D[0], I[0])):
            similarity_score = 1 - distance  # Convert distance to similarity
            if similarity_score >= 0.40:  # 40% threshold
                filtered_results.append((idx, similarity_score))
        
        # Right column - Show uploaded image in compact box
        with col2:
            st.markdown("**Your Upload:**")
            # Use container for better mobile layout
            with st.container():
                st.image(uploaded_file, caption="Uploaded Image", width=160)
        
        # Left column - Show recommendations in 2xn grid
        with col1:
            if filtered_results:
                st.markdown(f"**🔍 Recommended Products** ({len(filtered_results)} matches ≥40%):")
                
                # Create responsive 2xn grid layout with smaller images
                num_results = len(filtered_results)
                rows = (num_results + 1) // 2  # Calculate number of rows needed
                
                for row in range(rows):
                    cols = st.columns(2, gap="small")
                    for col_idx in range(2):
                        result_idx = row * 2 + col_idx
                        if result_idx < num_results:
                            idx, similarity_score = filtered_results[result_idx]
                            with cols[col_idx]:
                                img_path = image_paths[idx]
                                
                                # Create a compact container for better mobile responsiveness
                                with st.container():
                                    st.image(
                                        img_path, 
                                        caption=f"{similarity_score:.1%} match",
                                        width=150  # Smaller, more compact size
                                    )
            else:
                st.warning("🔍 No products found with 40% or higher similarity. Try a different image!")

    except Exception as e:
        st.error(f"❌ Failed to process uploaded image: {e}")

else:
    # Show placeholder when no image is uploaded
    st.info("👆 Upload an image above to get started!")
    
    # Optional: Show some sample product images in responsive grid
    if len(image_paths) > 0:
        st.markdown("**Sample Products Available:**")
        
        # Responsive sample grid
        sample_cols = st.columns([1, 1, 1, 1], gap="small")
        for i, col in enumerate(sample_cols):
            if i < min(4, len(image_paths)):  # Show max 4 samples
                with col:
                    st.image(image_paths[i], caption=f"Product {i+1}", width=120)