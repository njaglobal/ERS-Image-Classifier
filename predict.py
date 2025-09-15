import tensorflow as tf
import numpy as np
from PIL import Image
import io
import cv2
from exif import Image as ExifImage
import os

# Hugging Face
from transformers import BlipProcessor, BlipForConditionalGeneration
import torch

# Paths
MODEL_PATH = "models/final_model_latest.tflite"
LABELS_PATH = "models/labels_full.txt"
IMG_SIZE = (224, 224)

# ---- Load TFLite ResNet50 model ----
def load_model_and_labels():
    if not os.path.exists(MODEL_PATH):
        raise FileNotFoundError(f"Model file not found: {MODEL_PATH}")
    if not os.path.exists(LABELS_PATH):
        raise FileNotFoundError(f"Labels file not found: {LABELS_PATH}")
    
    with open(LABELS_PATH, "r") as f:
        class_labels = [line.strip() for line in f.readlines()]
    
    interpreter = tf.lite.Interpreter(model_path=MODEL_PATH)
    interpreter.allocate_tensors()
    input_details = interpreter.get_input_details()
    output_details = interpreter.get_output_details()
    
    return interpreter, input_details, output_details, class_labels

try:
    interpreter, input_details, output_details, class_labels = load_model_and_labels()
    print(f"✅ ResNet50-based model loaded successfully")
    print(f"📋 Available classes: {class_labels}")
except Exception as e:
    print(f"❌ Error loading model: {e}")
    interpreter = input_details = output_details = class_labels = None

# ---- Load Hugging Face BLIP model ----
try:
    device = "cuda" if torch.cuda.is_available() else "cpu"
    blip_processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
    blip_model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base").to(device)
    print("✅ BLIP captioning model loaded")
except Exception as e:
    print(f"❌ Error loading BLIP model: {e}")
    blip_processor = blip_model = None

# ---- Preprocess ----
def preprocess(image_bytes: bytes) -> np.ndarray:
    img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    img = img.resize(IMG_SIZE)
    img = np.array(img, dtype=np.float32) / 255.0
    return np.expand_dims(img, axis=0)

# ---- Fake photo detection ----
def is_likely_fake_photo(image_bytes: bytes) -> bool:
    is_fake = False
    try:
        exif = ExifImage(io.BytesIO(image_bytes))
        camera_make = getattr(exif, "make", "").lower()
        camera_model = getattr(exif, "model", "").lower()
        if any(k in camera_make for k in ["apple", "samsung", "xiaomi", "oppo", "vivo", "huawei", "google"]) or \
           any(k in camera_model for k in ["iphone", "galaxy", "pixel", "redmi", "android"]):
            is_fake = True
    except:
        pass

    try:
        pil_img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        np_img = np.array(pil_img)
        gray = cv2.cvtColor(np_img, cv2.COLOR_RGB2GRAY)
        laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
        if laplacian_var < 50:
            is_fake = True
    except:
        pass

    return is_fake

def is_ambiguous(output: np.ndarray, threshold: float = 0.15) -> bool:
    sorted_probs = np.sort(output[0])
    return (sorted_probs[-1] - sorted_probs[-2]) < threshold

# ---- BLIP caption generation ----
def generate_caption(image_bytes: bytes) -> str:
    if blip_model is None:
        return "No caption available"
    try:
        pil_img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        inputs = blip_processor(pil_img, return_tensors="pt").to(device)
        out = blip_model.generate(**inputs, max_length=50)
        caption = blip_processor.decode(out[0], skip_special_tokens=True)
        caption = caption.strip()
        if caption:
            caption = caption[0].upper() + caption[1:]

        return caption
    except Exception as e:
        return f"Captioning failed: {e}"

# ---- Final classification + caption fusion ----
def classify_and_describe(image_bytes: bytes) -> dict:
    if interpreter is None:
        return {"error": "Model not loaded"}

    # 1. Run ResNet50 classification
    input_data = preprocess(image_bytes)
    interpreter.set_tensor(input_details[0]['index'], input_data)
    interpreter.invoke()
    output = interpreter.get_tensor(output_details[0]['index'])

    predicted_idx = int(np.argmax(output))
    confidence = float(np.max(output))
    label = class_labels[predicted_idx]

    # 2. BLIP caption
    caption = generate_caption(image_bytes)

    # 3. Validity filters
    if label == "none-accident":
        return {
            "label": label,
            "confidence": round(confidence, 4),
            "status": "invalid",
            "action": "reject",
            "reason": "No visible incident",
            "caption": f"{caption}. No visible incident"
        }
    if is_likely_fake_photo(image_bytes):
        return {"label": label, "action": "reject", "status": "invalid", "reason": "Likely fake photo", "caption": f"{caption}. This is likely a Fake Photo."}
    if is_ambiguous(output):
        return {"label": "none-accident", "action": "uncertain", "status": "invalid", "reason": "Ambiguous", "caption": f"{caption}. This need human intervention."}
    if confidence < 0.75:
        return {"label": label, "action": "uncertain", "status": "invalid", "reason": "Low confidence Level, Needs Human review", "caption": f"{caption}. This need human intervention."}

    # 4. Merge intelligently
    merged_desc = caption
    if label == "fire":
        merged_desc += ". This appears to be a valid fire incident."
    elif label == "road":
        merged_desc += ". This seems to be a valid road accident or collision."

    return {
        "label": label,
        "confidence": round(confidence, 4),
        "status": "valid",
        "action": "accept",
        "reason": "Valid incident",
        "caption": merged_desc
    }