import os
import gdown

MODEL_PATH = "./routers/models/classifier"
MODEL_FILE = "model.safetensors"
os.makedirs(MODEL_PATH, exist_ok=True)
MODEL_FULL_PATH = os.path.join(MODEL_PATH, MODEL_FILE)

# Google Drive file ID
MODEL_ID = "1nEYz8cDm5b4vYigbBR5qtC-Ywm8TXihL"
GDRIVE_URL = f"https://drive.google.com/uc?id={MODEL_ID}"

if not os.path.exists(MODEL_FULL_PATH):
    print("⬇️ Downloading model from Google Drive...")
    gdown.download(GDRIVE_URL, MODEL_FULL_PATH, quiet=False)
    print("✅ Model downloaded.")
else:
    print("✅ Model already exists, skipping download.")
