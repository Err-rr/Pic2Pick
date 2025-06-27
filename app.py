import os
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

import streamlit as st
import numpy as np
import json
import faiss
import requests
from PIL import Image
from transformers import CLIPProcessor, CLIPModel

# Setup
st.set_page_config(page_title="Pic2Pick", layout="wide")
st.title("🖼️ Pic2Pick - Upload and Find Visually Similar Items")

# Load model
model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")

# Load category -> URLs
with open("data/image_urls.json", "r") as f:
    category_to_urls = json.load(f)

# Upload or URL
option = st.radio("Choose input method:", ["Upload an Image", "Paste Image URL"])
image = None

if option == "Upload an Image":
    uploaded_file = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png"])
    if uploaded_file:
        image = Image.open(uploaded_file).convert("RGB")
elif option == "Paste Image URL":
    url = st.text_input("Paste image URL:")
    if url:
        try:
            image = Image.open(requests.get(url, stream=True).raw).convert("RGB")
        except:
            st.error("Failed to load image.")

if image:
    st.image(image, caption="Query Image", use_container_width=True)

    # Generate query embedding
    inputs = processor(images=image, return_tensors="pt")
    query_feature = model.get_image_features(**inputs).detach().numpy()

    # 🔍 Auto-detect category by checking closest match across all categories
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

    if best_category is None:
        st.error("❌ Could not match your image to any category.")
    else:
        st.success(f"✅ Detected Category: **{best_category}**")

        # 🔁 Get top 20 matches and show up to 6 unique images
        features = np.load(f"data/features_{best_category}.npy")
        index = faiss.IndexFlatL2(features.shape[1])
        index.add(features)
        D, I = index.search(query_feature, k=20)

        st.subheader("Similar Items:")
        cols = st.columns(6)
        shown_urls = set()
        shown_count = 0

        for idx in I[0]:
            if idx >= len(best_urls):
             continue  # skip broken index
            url = best_urls[idx]
            if url in shown_urls:
                continue  # skip duplicates
            shown_urls.add(url)

            with cols[shown_count % 6]:
                st.image(url, use_container_width=True)
            shown_count += 1

            if shown_count >= 6:
                break
