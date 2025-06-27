import os
import json
import numpy as np
import requests
from PIL import Image
from tqdm import tqdm
from transformers import CLIPProcessor, CLIPModel

# Load CLIP model and processor
model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")

# Load original URLs
with open("data/image_urls.json", "r") as f:
    original_data = json.load(f)

# Prepare to save cleaned URLs
cleaned_data = {}

# Output directory
os.makedirs("data", exist_ok=True)

# Process each category
for category, urls in original_data.items():
    print(f"\n⏳ Processing category: {category} ({len(urls)} URLs)")

    valid_urls = []
    features = []

    for url in tqdm(urls, desc=f"Embedding {category}"):
        try:
            image = Image.open(requests.get(url, stream=True).raw).convert("RGB")
            inputs = processor(images=image, return_tensors="pt")
            outputs = model.get_image_features(**inputs)
            features.append(outputs[0].detach().numpy())
            valid_urls.append(url)
        except Exception as e:
            print(f"⚠️ Skipped {url}: {e}")

    # Save features and valid URLs
    if features:
        np.save(f"data/features_{category}.npy", np.vstack(features))
        cleaned_data[category] = valid_urls
        print(f"✅ Saved: {len(valid_urls)} valid images for '{category}'")
    else:
        print(f"❌ No valid images found for '{category}'")

# Save cleaned URL mapping
with open("data/valid_image_urls.json", "w") as f:
    json.dump(cleaned_data, f, indent=2)
    print("\n📝 Saved cleaned image URLs to valid_image_urls.json")
