# 📸 Pic2Pick - Visual Product Recommender

**Pic2Pick** is an AI-powered visual search engine that helps users find visually similar products just by uploading or linking an image. Designed for fast, accurate, and real-world e-commerce use cases, it's like "Shazam for shopping."

---

## 🚀 Features

* 🔍 **Search by Image:** Upload an image or paste a URL to find similar products
* 🤖 **CLIP Embedding:** Uses OpenAI's CLIP model to extract image features
* ⚖️ **Similarity Matching:** Finds top matching items using cosine similarity
* 🎨 **Color Similarity Add-on:** Bonus color match score based on dominant colors
* 🛍 **Buy Now Buttons:** Direct Amazon and Flipkart links for each match
* 🌐 **Cloud-Ready:** Lightweight, optimized for Streamlit Cloud deployment

---

## 🏗️ Project Structure

```bash
Pic2Pick/
├── app.py                     # Main Streamlit app
├── precompute_embeddings.py  # Script to generate product embeddings
├── data/
│   ├── raw_products.json     # Original product data (image URLs)
│   ├── product_data.csv      # Processed CSV with clip_vector
│   └── features_*.npy        # Optional: category-specific features
├── venv/                     # Python virtual environment (not pushed)
├── requirements.txt          # Required dependencies
└── README.md
```

---

## ⚙️ Installation

```bash
# Clone the repo
https://github.com/your-username/Pic2Pick.git
cd Pic2Pick

# Set up virtual environment
python -m venv venv
venv\Scripts\activate  # or source venv/bin/activate on macOS/Linux

# Install dependencies
pip install -r requirements.txt
```

---

## 🧠 How It Works

1. User uploads an image or pastes an image URL
2. The image is passed through the CLIP model → generates a 512D feature vector
3. This vector is compared against precomputed embeddings of product images
4. Cosine similarity is calculated
5. Top matches are shown with image, name, category, and links

---

## 🛠 Precompute Embeddings

```bash
python precompute_embeddings.py
```

> It loads image URLs from `raw_products.json`, computes CLIP embeddings, and writes to `product_data.csv`

---


## 🖥 Run the App

```bash
streamlit run app.py
```


## 👤 Author

Made by Shivam Kumar with ❤️ 

> "See It. Snap It. Get It."

---
